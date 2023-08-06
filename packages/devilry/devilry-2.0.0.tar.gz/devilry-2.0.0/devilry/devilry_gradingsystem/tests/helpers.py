from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from devilry.apps.core.models import StaticFeedback
from devilry.devilry_gradingsystem.models import FeedbackDraftFile
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class FeedbackEditorViewTestMixin(object):
    """
    Mixin class that makes it easier to test the FeedbackEditorView
    that each gradingsystem plugin must implement.
    """
    def login(self, user):
        self.client.login(username=user.username, password='test')

    def get_as(self, user):
        self.login(user)
        return self.client.get(self.url)

    def post_as(self, user, *args, **kwargs):
        self.login(user)
        return self.client.post(self.url, *args, **kwargs)

    def get_valid_post_data_without_feedbackfile_or_feedbacktext(self):
        """
        Must return a valid POST data dict with the plugin specific
        data (not feedbackfile, and not feedbacktext).
        """
        raise NotImplementedError()

    def get_empty_delivery_with_testexaminer_as_examiner(self):
        """
        Must return a delivery with no feedback. The user
        returned by :meth:`.get_testexaminer` must be
        registered as examiner on the group owning the delivery.
        """
        raise NotImplementedError()

    def get_testexaminer(self):
        """
        See :meth:`.get_empty_delivery_with_testexaminer_as_examiner`.
        """
        raise NotImplementedError()

    def test_post_with_feedbackfile_no_existing_file(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        self.assertEquals(delivery.feedbacks.count(), 0)
        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 0)

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = SimpleUploadedFile('testfile.txt', 'Feedback file test')
        self.post_as(testexaminer, postdata)

        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        feedbackdraftfile = FeedbackDraftFile.objects.get(delivery=delivery)
        self.assertEqual(feedbackdraftfile.filename, 'testfile.txt')
        self.assertEqual(feedbackdraftfile.file.read(), 'Feedback file test')

    def test_post_with_feedbackfile_has_existing_file(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='oldtestfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Oldfile'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = SimpleUploadedFile('testfile.txt', 'Feedback file test')
        self.post_as(testexaminer, postdata)

        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        feedbackdraftfile = FeedbackDraftFile.objects.get(delivery=delivery)
        self.assertEqual(feedbackdraftfile.filename, 'testfile.txt')
        self.assertEqual(feedbackdraftfile.file.read(), 'Feedback file test')

    def test_post_remove_feedbackfile(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='oldtestfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Oldfile'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = ''
        postdata['feedbackfile-clear'] = 'on'
        self.post_as(testexaminer, postdata)

        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 0)

    def test_post_update_draft_without_changing_feedbackfile(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='testfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Feedback file test'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = ''
        self.post_as(testexaminer, postdata)

        self.assertEquals(delivery.devilry_gradingsystem_feedbackdraft_set.count(), 1)
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        feedbackdraftfile = FeedbackDraftFile.objects.get(delivery=delivery)
        self.assertEqual(feedbackdraftfile.filename, 'testfile.txt')
        self.assertEqual(feedbackdraftfile.file.read(), 'Feedback file test')

    def test_post_with_feedbackfile_is_private(self):
        testexaminer = self.get_testexaminer()
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        feedbackdraftfile = FeedbackDraftFile(
            delivery=delivery,
            saved_by=UserBuilder('otheruser').user,
            filename='otherfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Other'))

        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['feedbackfile'] = SimpleUploadedFile('testfile.txt', 'Feedback file test')
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 1)
        self.post_as(testexaminer, postdata)
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery).count(), 2)
        self.assertEquals(FeedbackDraftFile.objects.filter(delivery=delivery, saved_by=testexaminer).count(), 1)

    def test_post_publish_with_feedbackfile(self):
        delivery = self.get_empty_delivery_with_testexaminer_as_examiner()
        testexaminer = self.get_testexaminer()
        feedbackdraftfile = FeedbackDraftFile(delivery=delivery, saved_by=testexaminer, filename='testfile.txt')
        feedbackdraftfile.file.save('unused.txt', ContentFile('Feedback file test'))
        postdata = self.get_valid_post_data_without_feedbackfile_or_feedbacktext()
        postdata['submit_publish'] = 'yes'

        self.assertEquals(StaticFeedback.objects.count(), 0)
        self.post_as(testexaminer, postdata)
        self.assertEquals(StaticFeedback.objects.count(), 1)
        staticfeedback = StaticFeedback.objects.get(delivery=delivery)
        self.assertEquals(staticfeedback.files.count(), 1)
        fileattachment = staticfeedback.files.first()
        self.assertEquals(fileattachment.filename, 'testfile.txt')
        self.assertEquals(fileattachment.file.read(), 'Feedback file test')
