import os


TEST_SOURCE = ''
TEST_DESTINATION = ''
TEST_DIRECTORY = 'temp'


def with_test_directories(func):
    '''
    Create directories for testing purposes.
    Then, delete them after the test is run.
    '''

    def inner(*args, **kwargs):

        # Define the source and destination directories
        source = 'test/test_folder/source',
        destination = 'test/test_folder/destination'
        directory = 'directory'

        # Create the test directories
        os.makedirs('test/test_folder/source', exist_ok=True)
        os.makedirs('test/test_folder/destination', exist_ok=True)

        # Create dummy files in them
        os.makedirs(
            os.path.join(destination, 'temp', 'daily.1'),
            exist_ok=True
        )

        with open(os.path.join(destination, 'temp', 'daily.1', 'file.txt'), 'w') as f:
            f.write('This is a dummy file')
        
        func(*args, **kwargs)

        # Delete the test directories
        os.removedirs('test/test_folder/source')
        os.removedirs('test/test_folder/destination')

    return inner
