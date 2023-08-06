from collections import defaultdict
import logging
logger = logging.getLogger(__name__)


TEST_CLASSES = {}
TEST_STAGES = defaultdict(lambda: [])
class TestRegistry(type):
    classes = TEST_CLASSES
    stages = TEST_STAGES
    blacklist_class_names = ['Testcase']

    def __new__(mcs, name, bases, class_dict):
        class_instance = type.__new__(mcs, name, bases, class_dict)
        if name in mcs.blacklist_class_names:
            logger.debug('skip %s', name)
            return class_instance
        # register in class-dict
        mcs.classes[name] = class_instance
        # register in stage-dict
        for stage in class_dict.get('stages', ['stage1']):
            mcs.stages[stage].append(name)
        logger.debug('registered: %s', name)
        return class_instance



__all__ = ['TestRegistry', 'TEST_CLASSES', 'TEST_STAGES']
