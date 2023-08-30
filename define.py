TEST_TIME = 'run-0'
DATABASE = 'ltdb/'
# DATABASE = 'mitdb/'
PROJECT_DIR = 'Result/'

SAVE_MODEL_DIR = PROJECT_DIR + 'model/' + DATABASE
TEMP_DIR = PROJECT_DIR + 'temp/'
TENSOR_BOARD_DIR = PROJECT_DIR + 'log/' + DATABASE
RESULT_DIR = PROJECT_DIR + 'result/' + DATABASE


LTDB_DIR = '/media/dev7/Data_1/Dataset/ltdb/'
MITDB_DIR = '/media/dev7/Data_1/Dataset/mitdb/'
AHADB_DIR = '/media/dev7/Data_1/Dataset/ahadb/'
ESCDB_DIR = '/media/dev7/Data_1/Dataset/escdb/'
NSTDB_DIR = '/media/dev7/Data_1/Dataset/nstdb/'

PREPROCESSED_DATA_DIR = '/media/dev7/Data_1/Dataset/trial_qrs_detection_dataset/' + DATABASE
CHECK_POINT_DIR = '/media/dev7/Data_1/Dataset/trial_qrs_detection_dataset/checkpoint/' + DATABASE

FREQUENCY_SAMPLING = 128
NEIGHBOUR_POINT = int(FREQUENCY_SAMPLING * 0.1) + int(FREQUENCY_SAMPLING * 0.3) + 1
POSITIVE_RANGE = int(FREQUENCY_SAMPLING * 0.04) + 1

DATA_TYPE = 'float64'
