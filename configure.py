from information import WorkInformation


if __name__ == '__main__':
    try:
        info = WorkInformation('configurator')
        print('Configures currently saved. You can now run main.py')
    except KeyboardInterrupt:
        print('Process of configure interrupted by user')
