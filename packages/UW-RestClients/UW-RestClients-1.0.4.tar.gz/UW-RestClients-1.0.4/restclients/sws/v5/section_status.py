from restclients.exceptions import InvalidSectionID
from restclients.sws.v5.section import section_label_pattern
from restclients.sws import get_resource, encode_section_label
from restclients.models.sws import SectionStatus

course_res_url_prefix = "/student/v5/course"

def get_section_status_by_label(label):
    import warnings
    warnings.warn("Totally untested against live resources!  Don't count on get_section_status_by_label in v5!")

    if not section_label_pattern.match(label):
        raise InvalidSectionID(label)

    url = "%s/%s/status.json" % (course_res_url_prefix,
                                 encode_section_label(label))

    return _json_to_sectionstatus(get_resource(url))

    pass

def _json_to_sectionstatus(section_data):
    """
    Returns a restclients.models.sws.SectionStatus object
    created from the passed json.
    """
    section_status = SectionStatus()
    if section_data["AddCodeRequired"] == 'true':
        section_status.add_code_required = True
    else:
        section_status.add_code_required = False
    section_status.current_enrollment = int(section_data["CurrentEnrollment"])
    section_status.current_registration_period = int(section_data["CurrentRegistrationPeriod"])
    if section_data["FacultyCodeRequired"] == 'true':
        section_status.faculty_code_required = True
    else:
        section_status.faculty_code_required = False
    section_status.limit_estimated_enrollment = int(section_data["LimitEstimateEnrollment"])
    section_status.limit_estimate_enrollment_indicator = section_data["LimitEstimateEnrollmentIndicator"]
    section_status.room_capacity = int(section_data["RoomCapacity"])
    section_status.sln = int(section_data["SLN"])
    section_status.space_available = int(section_data["SpaceAvailable"])
    if section_data["Status"] == "open":
        section_status.is_open = True
    else:
        section_status.is_open = False

    return section_status
