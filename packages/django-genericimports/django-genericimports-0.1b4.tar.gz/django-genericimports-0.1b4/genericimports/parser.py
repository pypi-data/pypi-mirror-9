# -*- coding: utf-8 -*-

# Python imports
import csv
from datetime import datetime
from distutils.util import strtobool
import logging
import os
import random
import string
import sys
import time

# Django imports
from django.db.models import get_model
from django.conf import settings
from django.core.mail import send_mail
from django.core.files import File

# Thirparty
from openpyxl import load_workbook
from dateutil.parser import parse as date_parser

# App modules
from exceptions import RowDataMalformed, FallOutOfRow, RecordAlreadyExists
from models import Report

# Speed/memory measurement as of 2015-01-16 on the development computer (sqlite):
# 2h15m / 350MB RAM for every 5k records.
# ~2.5 days / 7GB RAM for every 100k records.

# Create the logging instance
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = ['csv', 'xls', 'xlsx']


class Importer():

    def __init__(self, report_id, uploaded_file, querystring):

        """
        The init method should load the file from the upload form in the
        importhub, detect which filetype is and send it to the right task
        in django-rq to be processed.
        """
        # Save the querystring
        self.querystring = querystring
        # Set up the counters
        self.success = 0
        self.failed = 0
        self.existing = 0
        self.total = 0
        # Get the report
        self.report = Report.objects.get(id=report_id)
        self.report.status = 1
        # Set the files
        self.failed_file_name = "%s_%s_%s.csv" % (time.strftime("%Y%m%d"), time.strftime("%H%M"), 'failed_imports')
        self.fail_file = settings.MEDIA_ROOT + "/imports/" + self.failed_file_name
        # Start the timer
        self.start = datetime.now()
        if not uploaded_file:
            self.report.status = 3
            self.report.save()
            logger.error("ERROR 01: No file. Forcing exit.")
            sys.exit("Script failed execution. See logs.")
        else:
            # Detect the extension
            self.extension = uploaded_file.split('.')[-1]
            if self.extension in ALLOWED_EXTENSIONS:
                try:
                    # Create the folder if it doesn't exist
                    if not os.path.exists(os.path.dirname(self.fail_file)):
                        os.makedirs(os.path.dirname(self.fail_file))
                    # Open the error file to dump the failed rows
                    open_failed_file = open(self.fail_file, 'w')
                    self.failed_file = csv.writer(open_failed_file)
                except Exception as e:
                    self.report.status = 3
                    self.report.save()
                    logger.debug("Couldn't open the file to save the failed rows")
                    logger.error(e)
                try:
                    # Open the file in exclusive read-mode
                    self.f = open(uploaded_file)
                    if self.extension == 'csv':
                        # Send the CSV to the parser
                        self._process_csv(self.f)
                    else:
                        # Send the XLS to the parser
                        self._process_xls(self.f)
                except IOError as e:
                    self.report.status = 3
                    self.report.save()
                    logger.error("ERROR 03: Couldn't read the file. Forcing exit.")
                    logger.error(e)
                    sys.exit("Script failed execution. See logs.")
            else:
                logger.error("ERROR 02: Incorrect file extension. Forcing exit.")
                sys.exit("Script failed execution. See logs.")

    def _delete_row(self, rowdata):

        """Delete the data already inserted in the database

        This function gets called when there is a critical error on the row
        values and we should undo all the work that we did instead of trying
        to push it forward.
        """
        logger.warning("WARNING 01: A row failed, proceeding to deletion from DB.")
        # logger.warning(e)

        # Create record of this row on the output file
        logger.debug("Saving the failed row to the output file.")
        self.failed_file.writerow(rowdata)

        # Reverse the ID_LIST so we can go from top to bottom without
        # worring about foreignkeys. There are some use cases where the cascade
        # won't work correctly. We cannot use reverse() because it modifies
        # inplace.
        reversed_IDLIST = self.ID_LIST[::-1]
        reversed_mapping = settings.IMPORTER[0]['mapping'][::-1]

        for idx, i in enumerate(reversed_IDLIST):
            # Get model
            model = reversed_mapping[idx][0]['mapping']['model'].split('.')
            app_label = model[0]
            model_name = model[1]
            # Spawn the model
            try:
                model_instance = get_model(app_label=app_label, model_name=model_name)
                model_object = model_instance.objects.get(id=i)
                model_object.delete()
                logger.info("INFO 01: Successfully deleted row data from the DB")
            except:
                logger.error("Couldn't delete the object %s id: %s" % (model_name, i))
        # del self.ID_LIST[:]

    def _process_row(self, rowdata):

        """
        Process the row data according to the dictionary parameters. Full
        explanation follows:

        First we iterate over the entries (dictionary) in the settings, that's
        the mapping of fields and models. We get the model name and split
        it so we can instantiate it with get_model().

        After that we reset the position of the column counter (remember that
        we are operating with a single row here) and establish the row length
        __based on the mapping list__ not on the content. The reason for this
        is to avoid unnecesary iterations or fall outside of the list if the
        mapping is incorrect.

        Now for each column in the row, we iterate over the field mapping list
        determining first if it's an empty string or not. An empty string means
        that the models shouldn't store anything from that column, so we
        convert that into a True/False boolean. If the field is True, we populated
        the field in the model instance with the data that the column of the row
        gives us. This process is repeated over and over until all the model is
        filled with the data that we want.

        After all is populated we look for a foreignkey definition on the
        mapping that will tell us if the model is foreignkeyed to something,
        in special it will tell us the position of the related model in the
        mapping.
        """
        self.ID_LIST = []
        try:
            for entry in settings.IMPORTER[0]['mapping']:
                # Process the model name
                model = entry['model'].split('.')
                app_label = model[0]
                model_name = model[1]
                # Spawn the model
                model_instance = get_model(app_label=app_label, model_name=model_name)()
                # Reset column position
                current_column = 0
                # Get the length
                row_length = len(entry['fields'])
                # For each row throw a bunch of meta logic
                while current_column <= row_length - 1:
                    # print '%s - %s / %s' % (model_name, current_column, row_length - 1)

                    # See if we fall out of the list
                    current_field = entry['fields'][current_column]
                    try:
                        rowdata[current_column]
                    except IndexError:
                        current_column += 1
                        raise FallOutOfRow("This row in incomplete")

                    # Sanitize the row data
                    try:
                        rowdata_sanitized = unicode(rowdata[current_column], errors='ignore')
                    except UnicodeDecodeError as e:
                        logger.error("Column data malformed. Deleting and reporting the row.")
                        logger.error(e)
                        raise RowDataMalformed("Unable to sanitize the column value")

                    try:
                        # If the column in the mapping is empty, skip it. We do it by
                        # using the comparison "empty string = False"
                        if bool(current_field) and bool(rowdata_sanitized):
                            # Check if the field is a date
                            if type(current_field) == dict:
                                # Run the filter in the dict as a function
                                column_value = current_field['filter'](rowdata_sanitized)
                                # Rewrite current field name to match the dictionary value
                                current_field = entry['fields'][current_column]['name']
                            else:
                                # Get the metadata of the field
                                field_meta = model_instance._meta.get_field(current_field)
                                # Check if it the type is a boolean
                                if field_meta.get_internal_type() in ['BooleanField', 'NullBooleanField']:
                                    # Convert the string to a boolean, this shoudl cover most of the cases
                                    column_value = bool(strtobool(rowdata_sanitized))
                                # Check if the field is a date
                                elif field_meta.get_internal_type() in ['DateField', 'DateTimeField', 'TimeField']:
                                    # Parse the date in american format, it's the safest in programmatic terms
                                    column_value = date_parser(rowdata_sanitized)
                                # Is the field a choicefield?
                                elif field_meta.choices and type(field_meta.choices) == tuple:
                                    # Some magic to check which value corresponds to the label of the choice
                                    column_value = dict((key, value) for (value, key) in field_meta.choices)[rowdata_sanitized]
                                # The field doesn't have any choices
                                else:
                                    # Set the value to the direct value
                                    column_value = rowdata_sanitized

                            # logger.debug("Setting value %s = %s" % (current_field, column_value))
                            setattr(model_instance, current_field, column_value)
                        current_column += 1
                    # Any other exception that is not IndexError means corrupted data
                    except:
                        current_column += 1
                        raise RowDataMalformed("We have coprrupted data!")

                # Wait! Is there any unbound fields??
                if 'unbound' in entry:
                    # logger.debug("Processing unbound fields")
                    unbound_fields = entry['unbound']
                    try:
                        for field in unbound_fields:
                            # logger.debug("Going inside the unbound method loop")
                            try:
                                # Evaluate the code string! (Dangerous, needs revision)
                                unbound_method = eval(unbound_fields[field])
                            except:
                                logger.error("ERROR 06: Unbound method for %s invalid" % field)
                            # logger.debug("Setting ubound field value %s = %s" % (field, unbound_method))
                            setattr(model_instance, field, unbound_method)
                    except:
                        logger.error("ERROR 05: Unbound fields couldn't be populated")
                    # Save the object
                    # logger.debug("Lets save!")
                    try:
                        model_instance.save()
                    except Exception as e:
                        logger.error(e)

                if 'foreignkey' in entry:
                    # First of all we read the entry for the foreignkey, that defines
                    # the position of the foreign model in the IMPORTER list,
                    # the field to use as identifier and the field that FK's on
                    # our current side
                    fk_link = settings.IMPORTER[0]['mapping'][entry['foreignkey'][0]]
                    # Get the app name and model name
                    fk_model = fk_link['model'].split('.')
                    fk_app_label = fk_model[0]
                    fk_model_name = fk_model[1]
                    # We use get_model as a bridge to get the instance that we want
                    # from the object
                    try:
                        fk_instance = get_model(app_label=fk_app_label, model_name=fk_model_name)
                        fk_object = fk_instance.objects.get(id=self.ID_LIST[entry['foreignkey'][0]])
                        # Set the link field to the value of the foreign key
                        setattr(model_instance, entry['foreignkey'][1], fk_object)
                    except Exception as e:
                        logger.error(e)
                    # Finally, save that relation-ship!
                    try:
                        model_instance.save()
                    except Exception as e:
                        logger.error(e)

                # Check that there's not another copy of that object
                try:
                    model_instance.validate_unique()
                except Exception as e:
                    logger.warning("Record already exists in the database!: %s" % e)
                    raise RecordAlreadyExists("This data already exists")
                    # raise RowDataMalformed("Couln't validate unique fields")

                try:
                    model_instance.full_clean()
                except Exception as e:
                    logger.error("Object is invalid!: %s" % e)
                    if entry['optional']:
                        #fqall out of entryu continue on thwe next
                        raise FallOutOfRow("Object is invalid, but optional. Skipping to the next.")
                    else:
                        raise RowDataMalformed("Object has malformed data.")

                # After all the fields are populated, save the model instance
                try:
                    model_instance.save()
                    # Save the object id to the list
                    self.ID_LIST.append(model_instance.id)
                except Exception as e:
                    logger.error(e)
                    raise RowDataMalformed("Couldn't save the model!")

            # Success! Ousite of the entry loop, so it only counts full rows success
            self.success += 1
            # Add to the total
            self.total += 1

        except RowDataMalformed as e:
            self.failed += 1
            self.total += 1
            logger.error(e)
            logger.error("The data of this row is malformed.")
            self._delete_row(rowdata)

        except FallOutOfRow as e:
            # Success! Ousite of the entry loop, so it only counts full rows success
            self.success += 1
            # Add to the total
            self.total += 1
            logger.error(e)
            logger.error("We fell out of the list index. That means the row is shorter than the mapping!. Skipping to the next.")

        except RecordAlreadyExists as e:
            self.existing += 1
            self.total += 1
            logger.warning(e)

        except KeyboardInterrupt as e:
            self.report.status = 2
            self.report.save()
            logger.warning("Someone has cancelled the script manually")
            logger.warning(e)
            # Get basic stats
            self.end = datetime.now() - self.start
            print('Took: %s\nFailed: %s\nAdded: %s\nExisting: %s\n.Total:%s' % (self.end, self.failed, self.success, self.existing, self.total))
            # Stop the script
            sys.exit("User cancelled execution")

    def _process_csv(self, csvfile):

        """
        Once we detected that the file is a CSV, we pass it to this parser.
        The parser will load the dictionary set matching headers with fields
        and will start populating the database row by row.
        """
        reader = csv.reader(csvfile)
        map(self._process_row, reader)
        # [self._process_row(row) for row in reader]
        self.end = datetime.now() - self.start
        # Store the stats in an array with a specific order
        stats = [self.success, self.failed, self.existing, self.total]
        # Process report
        self._save_report(stats, self.failed_file)

    def _process_xls(self):
        pass

    def _save_report(self, stats, failedfile):

        """Save the report statistics and files

        This function will create a label for the report and store the statistics
        and the failed rows file.
        """
        try:
            self.report.total = stats[3]
            self.report.success = stats[0]
            self.report.failed = stats[1]
            self.report.existing = stats[2]
            self.report.label = datetime.now()
            failed_entries = File(open(self.fail_file, 'r'))
            self.report.failed_records.save(self.failed_file_name, failed_entries, save=True)
            self.report.status = 0
            self.report.save()

            # Run the callback
            settings.IMPORTER[0]['settings']['callback'](self.querystring)
        except:
            self.report.status = 3

        # send_mail('[ImportHub] Your import has finished',
        #          'Your CSV import has finished successfully. Here is the report:\n\n'
        #          'Took: %s\nFailed: %s\nAdded: %s\nExisting: %s\n.' % (
        #            self.end,self.failed,self.success,self.existing),
        #            'haha@example.com', ['oscar.carballal@havasww.com'],
        #            fail_silently=False)
