from django.db import models


class CanvasAccount(models.Model):
    account_id = models.IntegerField(max_length=20)
    sis_account_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=500)
    parent_account_id = models.CharField(max_length=30)
    root_account_id = models.CharField(max_length=30)

    class Meta:
        db_table = "restclients_canvas_account"


class CanvasRole(models.Model):
    role = models.CharField(max_length=200)
    base_role_type = models.CharField(max_length=200)
    workflow_state = models.CharField(max_length=50)

    class Meta:
        db_table = "restclients_canvas_role"


class CanvasTerm(models.Model):
    term_id = models.IntegerField(max_length=20)
    sis_term_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)

    # XXX - should this fall back to fetching from the SWS?
    def get_start_date(self):
        if self._start_date:
            return self._start_date
        raise Exception("Need to fetch this from the SWS, or manually pre-populate")

    def get_end_date(self):
        if self._end_date:
            return self._end_date
        raise Exception("Need to fetch this from the SWS, or manually pre-populate")

    class Meta:
        db_table = "restclients_canvas_term"


class CanvasCourse(models.Model):
    course_id = models.IntegerField(max_length=20)
    sis_course_id = models.CharField(max_length=100, null=True)
    account_id = models.IntegerField(max_length=20)
    term = models.ForeignKey(CanvasTerm, null=True)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    course_url = models.CharField(max_length=2000)
    workflow_state = models.CharField(max_length=50)
    public_syllabus = models.NullBooleanField()
    syllabus_body = models.TextField(null=True)

    def sws_course_id(self):
        if self.sis_course_id is None:
            return None

        parts = self.sis_course_id.split("-")
        if len(parts) != 5:
            return None

        sws_id = "%s,%s,%s,%s/%s" % (parts[0], parts[1], parts[2], parts[3],
                                     parts[4])

        return sws_id

    class Meta:
        db_table = "restclients_canvas_course"


class CanvasSection(models.Model):
    section_id = models.IntegerField(max_length=20)
    sis_section_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=200)
    course_id = models.IntegerField(max_length=20)
    nonxlist_course_id = models.IntegerField(max_length=20)

    class Meta:
        db_table = "restclients_canvas_section"


class CanvasEnrollment(models.Model):
    STUDENT = "StudentEnrollment"
    TEACHER = "TeacherEnrollment"
    TA = "TaEnrollment"
    OBSERVER = "ObserverEnrollment"
    DESIGNER = "DesignerEnrollment"

    ROLE_CHOICES = (
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
        (TA, "TA"),
        (OBSERVER, "Observer"),
        (DESIGNER, "Designer")
    )

    user_id = models.IntegerField(max_length=20)
    course_id = models.IntegerField(max_length=20)
    section_id = models.IntegerField(max_length=20)
    login_id = models.CharField(max_length=80)
    sis_user_id = models.CharField(max_length=32, null=True)
    role = models.CharField(max_length=80, choices=ROLE_CHOICES)
    status = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    html_url = models.CharField(max_length=1000)
    sis_section_id = models.CharField(max_length=100, null=True)
    sis_course_id = models.CharField(max_length=100, null=True)
    course_url = models.CharField(max_length=2000, null=True)
    course_name = models.CharField(max_length=100, null=True)
    current_score = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_score = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_grade = models.TextField(max_length=12, null=True)
    final_grade = models.TextField(max_length=12, null=True)
    grade_html_url = models.CharField(max_length=1000)
    total_activity_time = models.IntegerField(max_length=10, null=True)
    last_activity_at = models.DateTimeField(null=True) 

    def sws_course_id(self):
        if self.sis_course_id is None:
            return None

        parts = self.sis_course_id.split("-")

        if len(parts) != 5:
            return None

        sws_id = "%s,%s,%s,%s/%s" % (parts[0], parts[1], parts[2], parts[3],
                                     parts[4])

        return sws_id

    def json_data(self):
        return {"user_id": self.user_id,
                "course_id": self.course_id,
                "section_id": self.section_id,
                "login_id": self.login_id,
                "sis_user_id": self.sis_user_id,
                "role": self.role,
                "status": self.status,
                "current_score": self.current_score,
                "final_score": self.final_score,
                "current_grade": self.current_grade,
                "final_grade": self.final_grade}

    class Meta:
        db_table = "restclients_canvas_enrollment"


class Attachment(models.Model):
    attachment_id = models.IntegerField(max_length=20)
    filename = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    content_type = models.CharField(max_length=50)
    size = models.IntegerField(max_length=20)
    url = models.CharField(max_length=500)

    class Meta:
        db_table = "restclients_canvas_attachment"


class Report(models.Model):
    report_id = models.IntegerField(max_length=20)
    account_id = models.IntegerField(max_length=20)
    type = models.CharField(max_length=500)
    url = models.CharField(max_length=500)
    status = models.CharField(max_length=50)
    progress = models.SmallIntegerField(max_length=3, default=0)
    attachment = models.ForeignKey(Attachment, null=True)

    class Meta:
        db_table = "restclients_canvas_report"


class ReportType(models.Model):
    PROVISIONING = "provisioning_csv"
    SIS_EXPORT = "sis_export_csv"
    UNUSED_COURSES = "unused_courses_csv"

    NAME_CHOICES = (
        (PROVISIONING, "Provisioning"),
        (SIS_EXPORT, "SIS Export"),
        (UNUSED_COURSES, "Unused Courses")
    )

    name = models.CharField(max_length=500, choices=NAME_CHOICES)
    title = models.CharField(max_length=500)

    class Meta:
        db_table = "restclients_canvas_reporttype"


class SISImport(models.Model):
    CSV_IMPORT_TYPE = "instructure_csv"

    import_id = models.IntegerField(max_length=20)
    workflow_state = models.CharField(max_length=100)
    progress = models.CharField(max_length=3)

    class Meta:
        db_table = "restclients_canvas_sisimport"


class CanvasUser(models.Model):
    user_id = models.IntegerField(max_length=20)
    name = models.CharField(max_length=100, null=True)
    short_name = models.CharField(max_length=100, null=True)
    sortable_name = models.CharField(max_length=100, null=True)
    sis_user_id = models.CharField(max_length=100, null=True)
    login_id = models.CharField(max_length=100, null=True)
    time_zone = models.CharField(max_length=100, null=True)
    locale = models.CharField(max_length=2, null=True)
    email = models.CharField(max_length=100, null=True)
    avatar_url = models.CharField(max_length=500, null=True)

    def post_data(self):
        return {"user": {"name": self.name,
                         "short_name": self.short_name,
                         "sortable_name": self.sortable_name,
                         "time_zone": self.time_zone,
                         "locale": self.locale},
                "pseudonym": {"unique_id": self.login_id,
                              "sis_user_id": self.sis_user_id,
                              "send_confirmation": False}}

    class Meta:
        db_table = "restclients_canvas_user"


class Login(models.Model):
    login_id = models.IntegerField(max_length=20)
    account_id = models.IntegerField(max_length=20)
    sis_user_id = models.CharField(max_length=100, null=True)
    unique_id = models.CharField(max_length=100, null=True)
    user_id = models.IntegerField(max_length=20)

    def put_data(self):
        return {"login": {"unique_id": self.unique_id,
                          "sis_user_id": self.sis_user_id}}

    class Meta:
        db_table = "restclients_canvas_login"


class CanvasAdmin(models.Model):
    admin_id = models.IntegerField(max_length=20)
    role = models.CharField(max_length=100)
    user = models.ForeignKey(CanvasUser)

    class Meta:
        db_table = "restclients_canvas_admin"


class Submission(models.Model):
    submission_id = models.IntegerField(max_length=20)
    body = models.TextField(null=True)
    attempt = models.IntegerField(max_length=2)
    submitted_at = models.DateTimeField()
    assignment_id = models.IntegerField(max_length=20)
    workflow_state = models.CharField(max_length=100, null=True)
    preview_url = models.CharField(max_length=500)
    late = models.NullBooleanField()
    grade = models.TextField(max_length=12, null=True)
    score = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    grade_matches_current_submission = models.NullBooleanField()
    url = models.CharField(max_length=500, null=True)
    grader_id = models.IntegerField(max_length=20)
    graded_at = models.DateTimeField(null=True)
    submission_type = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = "restclients_canvas_submission"


class Assignment(models.Model):
    assignment_id = models.IntegerField(max_length=20)
    course_id = models.IntegerField(max_length=20)
    integration_id = models.CharField(max_length=200)
    integration_data = models.CharField(max_length=1500)
    due_at = models.DateTimeField(null=True)
    points_possible = models.IntegerField(max_length=8)
    grading_type = models.CharField(max_length=20)
    grading_standard_id = models.IntegerField(max_length=20, null=True)
    position = models.IntegerField(max_length=8)
    name = models.CharField(max_length=500)
    muted = models.NullBooleanField()
    html_url = models.CharField(max_length=500, null=True)

    def json_data(self):
        return {"assignment": {
                "integration_id": self.integration_id,
                "integration_data": self.integration_data}}

    class Meta:
        db_table = "restclients_canvas_assignment"


class Quiz(models.Model):
    quiz_id = models.IntegerField(max_length=20)
    due_at = models.DateTimeField()
    title = models.CharField(max_length=500)
    html_url = models.CharField(max_length=500, null=True)
    published = models.NullBooleanField()

    class Meta:
        db_table ="restclients_canvas_quiz"


class GradingStandard(models.Model):
    COURSE_CONTEXT = "Course"
    ACCOUNT_CONTEXT = "Account"

    CONTEXT_CHOICES = (
        (COURSE_CONTEXT, COURSE_CONTEXT),
        (ACCOUNT_CONTEXT, ACCOUNT_CONTEXT)
    )

    grading_standard_id = models.IntegerField(max_length=20)
    title = models.CharField(max_length=500)
    context_id = models.IntegerField(max_length=20)
    context_type = models.CharField(max_length=20, choices=CONTEXT_CHOICES)
    grading_scheme = models.TextField()


class DiscussionTopic(models.Model):
    topic_id = models.IntegerField(max_length=20)
    html_url = models.CharField(max_length=500, null=True)
    course_id = models.IntegerField()


class DiscussionEntry(models.Model):
    entry_id = models.IntegerField()
    user_id = models.IntegerField()
