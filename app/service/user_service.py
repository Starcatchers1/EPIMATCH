from app.utils.scrape_util import normalize_string
from app.extensions import db
from ..models import *

"""
User Service class: This class handles all the logic relating to the user model.
"""


def save_user(user_info, new_user=False):
    """
    Stores parsed user data
    Returns `id`(public_id) of saved user
    """
    personal_info = user_info["personal_info"]
    personal_info["signedup"] = new_user
    """Create user"""
    user = User()
    user.from_dict(personal_info)
    db.session.add(user)
    # Writes out all pending object actions to the database
    db.session.flush()

    """Create certifications association"""
    experiences = user_info["experiences"]
    certifications = experiences["certifications"]
    for _certification in certifications:
        certification = Certification()
        data = {
            'title': _certification["title"],
            'authority': _certification["authority"],
            'date_range': _certification["date_range"],
            'user_id': user.id
        }
        certification.from_dict(data)
        db.session.add(certification)
        # link to user
        user.add_certification(certification)
    db.session.flush()

    """Create course association"""
    accomplishments = user_info["accomplishments"]
    courses = accomplishments["courses"]
    for _course in courses:
        course = Course()
        data = {'name': _course, 'user_id': user.id}
        course.from_dict(data)
        db.session.add(course)
        user.add_course(course)
    db.session.flush()

    """Create honor association"""
    honors = accomplishments["honors"]
    for _honor in honors:
        honor = Honor()
        data = {'title': _honor, 'user_id': user.id}
        honor.from_dict(data)
        db.session.add(honor)
        user.add_honor(honor)
    db.session.flush()

    """Create language association"""
    languages = accomplishments["languages"]
    for _language in languages:
        language = Language()
        data = {'language': _language, 'user_id': user.id}
        language.from_dict(data)
        db.session.add(language)
        user.add_language(language)
    db.session.flush()

    """Create organization association"""
    organizations = accomplishments["organizations"]
    for _organization in organizations:
        organization = Organization()
        data = {'name': _organization, 'user_id': user.id}
        organization.from_dict(data)
        db.session.add(organization)
        user.add_organization(organization)
    db.session.flush()

    """Create patent association"""
    patents = accomplishments["patents"]
    for _patent in patents:
        patent = Patent()
        data = {'name': _patent, 'user_id': user.id}
        patent.from_dict(data)
        db.session.add(patent)
        user.add_patent(patent)
    db.session.flush()

    """Create project association"""
    projects = accomplishments["projects"]
    for _project in projects:
        project = Project()
        data = {'name': _project, 'user_id': user.id}
        project.from_dict(data)
        db.session.add(project)
        user.add_project(project)
    db.session.flush()

    """Create publication association"""
    publications = accomplishments["publications"]
    for _publication in publications:
        publication = Publication()
        data = {'title': _publication, 'user_id': user.id}
        publication.from_dict(data)
        db.session.add(publication)
        user.add_publication(publication)
    db.session.flush()

    """Create text_scores association"""
    text_scores = accomplishments["text_scores"]
    for _text_score in text_scores:
        text_score = TextScore()
        data = {
            'name': _text_score["name"],
            'score': _text_score["score"],
            'user_id': user.id
        }
        text_score.from_dict(data)
        db.session.add(text_score)
        user.add_text_score(text_score)
    db.session.flush()

    """Create Volunteer association"""
    volunteering_data = experiences["volunteering"]
    for _volunteer in volunteering_data:
        volunteer = Volunteer()
        data = {
            'organization': _volunteer["company"],
            'title': _volunteer["title"],
            'date_range': _volunteer["date_range"],
            'cause': _volunteer["cause"],
            'location': _volunteer["location"],
            'user_id': user.id
        }
        volunteer.from_dict(data)
        db.session.add(volunteer)
        user.add_volunteering(volunteer)
    db.session.flush()

    """Create website association"""
    websites = personal_info["websites"]
    for _website in websites:
        website = Website()
        data = {'url': _website, 'user_id': user.id}
        website.from_dict(data)
        db.session.add(website)
        user.add_website(website)
    db.session.flush()

    """Create Company & Job association"""
    jobs = experiences["jobs"]
    for _job in jobs:
        company_name = _job["company"].split('\n')[0].strip()
        company = Company.query.filter_by(
            name=company_name).first()
        if not company:
            company = Company()
            data = {
                'name': company_name,
                'url': _job["li_company_url"]
            }
            company.from_dict(data)
            db.session.add(company)
            db.session.flush()
        user_job = Job()
        data = {
            'title': _job["title"],
            'date_range': _job["date_range"],
            'location': _job["location"],
            'current': company.name == personal_info["company"],
            'user_id': user.id,
            'company_id': company.id,
            'company': company
        }
        user_job.from_dict(data)
        user.jobs.append(user_job)
    db.session.flush()

    """Create Education & association"""
    education_data = experiences["education"]
    for _education in education_data:
        school_name = _education["name"]
        education = Education.query.filter_by(
            school=school_name).first()
        if not education:
            education = Education()
            education.school = school_name
            db.session.add(education)
            db.session.flush()
        user_education = UserEducationAssociation()
        data = {
            'education_id': education.id,
            'user_id': user.id,
            'degree': _education["degree"],
            'field_of_study': _education["field_of_study"],
            'date_range': _education["date_range"],
            'grades': _education["grades"],
            'education': education
        }
        user_education.from_dict(data)
        user.education_history.append(user_education)
    db.session.flush()

    """Create interests association"""
    interests = user_info["interests"]
    for _interest in interests:
        interest = Interest.query.filter_by(name=_interest).first()
        if not interest:
            interest = Interest()
            interest.name = _interest
            db.session.add(interest)
            db.session.flush()
        user_interest = UserInterestAssociation()
        data = {
            'interest_id': interest.id,
            'user_id': user.id,
            'interest': interest
        }
        user_interest.from_dict(data)
        user.interests.append(user_interest)
    db.session.flush()

    """Create Skills & association"""
    skills = user_info["skills"]
    for _skill in skills:
        skill_name = _skill["name"]
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            skill = Skill()
            skill.name = skill_name
            db.session.add(skill)
            db.session.flush()
        user_skill = UserSkillAssociation()
        data = {
            'endorsements': _skill["endorsements"],
            'user_id': user.id,
            'skill_id': skill.id,
            'skill': skill
        }
        user_skill.from_dict(data)
        user.skills.append(user_skill)
    db.session.commit()

    return user.public_id


def get_current_user_by_id(user_public_id):
    """Search user by public_id & Return user"""
    user = User.query.filter_by(public_id=user_public_id).first()
    if not user:
        return None

    return user


def get_current_user_by_url(user_url):
    """Search user by url & Return user"""
    user = User.query.filter_by(url=user_url).first()
    if not user:
        return None

    return user


def get_top_skills_keyword_text(user_public_id, max_count=4):
    """
    ToDo:
    Get Skills from DB(if no skills= > use any other field)
    """
    user = get_current_user_by_id(user_public_id)
    if not user:
        print('No such user')
        return []

    skills = list(map(lambda x: x.skill.name, user.skills))
    # Get some top skills
    keywords = skills[:min(len(skills), max_count)]

    return keywords


def save_search_result(url, user):
    """
    Save & Associate search result urls with current user
    Returns void
    """
    """Create SearchResultPerson & association"""
    search_result_person = SearchResultPerson.query.filter_by(
        url=url).first()
    if not search_result_person:
        search_result_person = SearchResultPerson()
        search_result_person.from_dict({'url': url})
        db.session.add(search_result_person)
        db.session.flush()

    user_mapping = SearchResultPersonAssociation.query.filter_by(
        user_id=user.id, search_result_person_id=search_result_person.id).first()
    if not user_mapping:
        user_mapping = SearchResultPersonAssociation()
        data = {
            'search_result_person_id': search_result_person.id,
            'user_id': user.id,
            'search_result': search_result_person
        }
        user_mapping.from_dict(data)
        user.search_results.append(user_mapping)
    db.session.commit()


def get_all_user_skills(skills):
    """Returns list of user skills"""
    def build(item):
        return {
            'endorsements': item.endorsements,
            **item.skill.to_dict()  # spread dictionary
        }

    result = list(map(build, skills))

    return result


def get_user_education_history(education):
    """Returns list of user education"""
    def build(item):
        return {
            'degree': item.degree,
            'field_of_study': item.field_of_study,
            'date_range': item.date_range,
            'grades': item.grades,
            **item.education.to_dict(),  # spread dictionary
            'created_at': item.created_at,
            'updated_at': item.updated_at
        }

    result = list(map(build, education))

    return result


def get_user_jobs_history(jobs):
    """Returns list of user's job history"""
    def build(item):
        return {
            'title': item.title,
            'date_range': item.date_range,
            'location': item.location,
            'current': item.current,
            **item.company.to_dict(),  # spread dictionary
            'created_at': item.created_at,
            'updated_at': item.updated_at
        }

    result = list(map(build, jobs))

    return result


def get_full_user(user):
    data = {}

    personal_info = user.to_dict()
    data["personal_info"] = personal_info
    personal_info["websites"] = list(
        map(lambda x: x.to_dict(), user.websites))

    experiences = {}
    experiences["certifications"] = list(
        map(lambda x: x.to_dict(), user.certifications))
    experiences["volunteering"] = list(
        map(lambda x: x.to_dict(), user.volunteering))
    experiences["jobs"] = get_user_jobs_history(user.jobs)
    experiences["education"] = get_user_education_history(
        user.education_history)

    accomplishments = {}
    accomplishments["courses"] = list(
        map(lambda x: x.to_dict(), user.courses)
    )
    accomplishments["honors"] = list(
        map(lambda x: x.to_dict(), user.honors)
    )
    accomplishments["languages"] = list(
        map(lambda x: x.to_dict(), user.languages)
    )
    accomplishments["organizations"] = list(
        map(lambda x: x.to_dict(), user.organizations)
    )
    accomplishments["patents"] = list(
        map(lambda x: x.to_dict(), user.patents)
    )
    accomplishments["projects"] = list(
        map(lambda x: x.to_dict(), user.projects)
    )
    accomplishments["publications"] = list(
        map(lambda x: x.to_dict(), user.publications)
    )
    accomplishments["text_scores"] = list(
        map(lambda x: x.to_dict(), user.text_scores)
    )

    interests = list(
        map(lambda x: x.interest.to_dict(), user.interests))

    skills = get_all_user_skills(user.skills)

    data["experiences"] = experiences
    data["accomplishments"] = accomplishments
    data["interests"] = interests
    data["skills"] = skills

    return data


def get_search_results(search_results):
    """
    Returns list of search result
    """
    # iterate through child objects via association, including association attributes
    result = list(map(lambda x: x.search_result.to_dict(), search_results))

    return result


def get_all_user_recommendations(recommendations):
    """Returns list of recommended users"""
    result = list(map(lambda x: get_full_user(x.recommended), recommendations))

    return result


def normalize_new_user_data(request_data):
    """
    Building required fields to save to db
    """
    new_user = {
        "accomplishments": {
            "courses": [],
            "honors": [],
            "languages": [],
            "organizations": [],
            "patents": [],
            "projects": [],
            "publications": [],
            "text_scores": []
        },
        "experiences": {
            "certifications": [],
            "education": [],
            "jobs": [],
            "volunteering": []
        },
        "interests": [],
        "personal_info": {
            "company": "",
            "connected": "",
            "connections": 0,
            "current_company_link": "",
            "email": request_data["email"],
            "headline": request_data["headline"],
            "image": "https://i.imgur.com/vRai7J0.png",  # default avatar image url
            "location": request_data["location"],
            "name": request_data["name"],
            "phone": request_data["phone"],
            "school": "",
            "summary": "",
            # stored as an alternative for linkedin url
            "url": request_data["email"],
            "websites": []
        },
        "skills": []
    }

    def parse_skills(skill):
        return {'name': normalize_string(skill), 'endorsements': 0}

    new_user["skills"] = list(
        map(parse_skills, request_data["skills"]))

    return new_user
