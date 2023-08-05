__author__ = 'Corey Lin'

import os
import logging
from man_page_PyXB import *
from ConfigurationByUser import *


class CompareManPages:
    ATTRIBUTES_NEED_COMPARE = ["specificProblem", "alarmText", "probableCause", "alarmType", "meaning", "effect",
                               "supplementaryInformationFields", "instructions", "cancelling", "perceivedSeverityInfo"]

    IGNORE_ADAPTATION_REF = True

    MAN_PAGE_SUFFIX = ".man"

    LOG_LINE_SPLITTER = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    def __init__(self, result_file_name="man_pages_compare_result.txt"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        result_file_path = current_dir + os.sep + result_file_name
        if os.path.isfile(result_file_path):
            os.remove(result_file_path)
        logging.basicConfig(filename=result_file_path, level=logging.DEBUG,
                            format="%(asctime)s:%(levelname)s: %(message)s")

    def compare_man_pages_from_two_folders(self, folder_one_path, folder_two_path):
        self.folder_one_path = folder_one_path
        self.folder_two_path = folder_two_path
        man_page_names_folder_one = self._get_man_page_names_from_folder(folder_one_path)
        man_page_names_folder_two = self._get_man_page_names_from_folder(folder_two_path)
        self._compare_man_pages_from_two_sets(man_page_names_folder_one, man_page_names_folder_two)

    def _get_man_page_names_from_folder(self, folder_path):
        man_page_names = set(
            filter(lambda x: x.endswith("%s" % CompareManPages.MAN_PAGE_SUFFIX), os.listdir(folder_path)))
        return man_page_names

    def _compare_man_pages_from_two_sets(self, man_page_names_folder_one, man_page_names_folder_two):
        man_page_name_set = self._get_set_of_same_name_man_page(man_page_names_folder_one, man_page_names_folder_two)
        for man_page_name in man_page_name_set:
            self._compare_two_man_pages_of_same_name(man_page_name, self.folder_one_path, self.folder_two_path)

    def _get_set_of_same_name_man_page(self, man_page_names_folder_one, man_page_names_folder_two):
        return man_page_names_folder_one.intersection(man_page_names_folder_two)

    def _compare_two_man_pages_of_same_name(self, man_page_name, folder_one_path, folder_two_path):
        self.current_compare_man_page_name = man_page_name
        man_page_one_path = folder_one_path + os.sep + man_page_name
        man_page_two_path = folder_two_path + os.sep + man_page_name
        man_page_instance_one = alarm_description.CreateFromDocument(file(man_page_one_path).read())
        man_page_instance_two = alarm_description.CreateFromDocument(file(man_page_two_path).read())
        self._compare_two_man_page_instances(man_page_instance_one, man_page_instance_two)

    def _compare_two_man_page_instances(self, man_page_instance_one, man_page_instance_two):
        self._compare_alarm_description_attributes(man_page_instance_one, man_page_instance_two)
        if CompareManPages.IGNORE_ADAPTATION_REF is False:
            self._compare_adaptation_href(man_page_instance_one, man_page_instance_two)

    def _compare_adaptation_href(self, man_page_instance_one, man_page_instance_two):
        adap_href_one = man_page_instance_one.Adaptation.href
        adap_href_two = man_page_instance_two.Adaptation.href
        if adap_href_one != adap_href_two:
            logging.error(
                'Attribute "Adaptation.href" values are different:\nvalue is "%s" in %s\nvalue is "%s" in %s\n%s' % (
                    adap_href_one, self.folder_one_path + os.sep + self.current_compare_man_page_name, adap_href_two,
                    self.folder_two_path + os.sep + self.current_compare_man_page_name,
                    CompareManPages.LOG_LINE_SPLITTER))

    def _compare_alarm_description_attributes(self, man_page_instance_one, man_page_instance_two):
        for attribute in CompareManPages.ATTRIBUTES_NEED_COMPARE:
            self._compare_one_attribute_for_two_man_page_instances(attribute, man_page_instance_one,
                                                                   man_page_instance_two)

    def _compare_one_attribute_for_two_man_page_instances(self, attribute, man_page_instance_one,
                                                          man_page_instance_two):
        exist_status = self._check_attribute_exist_for_both_instances(attribute, man_page_instance_one,
                                                                      man_page_instance_two)
        if exist_status:
            self._check_attribute_value_for_both_instances(attribute, man_page_instance_one, man_page_instance_two)

    def _get_attribute_exist_status_for_both_instances(self, attribute, man_page_instance_one, man_page_instance_two):
        if getattr(man_page_instance_one, attribute) is not None:
            exist_for_instance_one = True
        else:
            exist_for_instance_one = False
        if getattr(man_page_instance_two, attribute) is not None:
            exist_for_instance_two = True
        else:
            exist_for_instance_two = False
        return exist_for_instance_one, exist_for_instance_two

    def _check_attribute_exist_for_both_instances(self, attribute, man_page_instance_one, man_page_instance_two):
        exist_for_instance_one, exist_for_instance_two = self._get_attribute_exist_status_for_both_instances(attribute,
                                                                                                             man_page_instance_one,
                                                                                                             man_page_instance_two)

        if exist_for_instance_one and (not exist_for_instance_two):
            logging.error('Attribute "%s":\nexist in %s\nmissing from %s\n%s', attribute,
                          self.folder_one_path + os.sep + self.current_compare_man_page_name,
                          self.folder_two_path + os.sep + self.current_compare_man_page_name,
                          CompareManPages.LOG_LINE_SPLITTER)
            return False
        elif (not exist_for_instance_one) and exist_for_instance_two:
            logging.error('Attribute "%s":\nmissing from %s\nexist in %s\n%s' % (
                attribute, self.folder_one_path + os.sep + self.current_compare_man_page_name,
                self.folder_two_path + os.sep + self.current_compare_man_page_name, CompareManPages.LOG_LINE_SPLITTER))
            return False
        elif (not exist_for_instance_one) and (not exist_for_instance_two):
            return False
        else:
            return True

    def _check_attribute_value_for_both_instances(self, attribute, man_page_instance_one, man_page_instance_two):
        attribute_value_one = getattr(man_page_instance_one, attribute)
        attribute_value_two = getattr(man_page_instance_two, attribute)
        if attribute_value_one != attribute_value_two:
            logging.error('Attribute "%s" values are different:\nvalue is "%s" in %s\nvalue is "%s" in %s\n%s' % (
                attribute, attribute_value_one, self.folder_one_path + os.sep + self.current_compare_man_page_name,
                attribute_value_two, self.folder_two_path + os.sep + self.current_compare_man_page_name,
                CompareManPages.LOG_LINE_SPLITTER))


if __name__ == '__main__':
    compare = CompareManPages()
    compare.compare_man_pages_from_two_folders(FOLDER_ONE_PATH, FOLDER_TWO_PATH)