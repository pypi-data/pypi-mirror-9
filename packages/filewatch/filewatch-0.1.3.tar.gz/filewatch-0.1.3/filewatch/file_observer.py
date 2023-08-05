from filewatch.observer import Subject

class FileUpdatedSubject(Subject):
    """Broadcast a list of updated files"""
    def notify(self, *args, **kwargs):
        file_list = kwargs['file_list']
        for observer in self.observers:
            # As we don't know what the observers will do to our filelist,
            # create a local copy so they all get the same list
            local_file_list = file_list[:]
            observer.notify(file_list=local_file_list)

file_updated_subject = FileUpdatedSubject()
# We only ever want one subject available, so remove the original class
# from the namespace
del FileUpdatedSubject