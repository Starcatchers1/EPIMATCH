from .ResultsObject import ResultsObject

from ..utils.scrape_util import *


class Profile(ResultsObject):
    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests']

    @property
    def personal_info(self):
        """Return dict of personal info about the user"""
        top_card = first_or_default(self.soup, '.pv-top-card')
        contact_info = first_or_default(self.soup, '.pv-contact-info')

        # Note that some of these selectors may have multiple selections, but
        # get_info takes the first match
        personal_info = get_info(top_card, {
            'name': '.pv-top-card--list > li',
            'headline': '.flex-1.mr5 h2',
            'company': 'li a[data-control-name="position_see_more"]',
            'school': 'li a[data-control-name="education_see_more"]',
            'location': '.pv-top-card--list-bullet > li',
        })

        personal_info['summary'] = text_or_default(
            self.soup, '.pv-about-section .pv-about__summary-text', '').replace('... see more', '').strip()

        image_url = ''
        # self profile image
        image_element = first_or_default(
            top_card, 'img.profile-photo-edit__preview')
        # find field of other user
        if not image_element:
            image_element = first_or_default(
                top_card, 'img.pv-top-card__photo')

        # Set image url to the src of the image html tag, if it exists
        try:
            image_url = image_element['src']
        except:
            pass

        personal_info['image'] = image_url

        connections_text = text_or_default(
            self.soup, 'a[data-control-name="topcard_view_all_connections"] span', '')
        if connections_text == '':
            connections_text = text_or_default(
                self.soup, '.pv-top-card--list-bullet:nth-child(3) > li:nth-child(2) > span:nth-child(1)', '0')  # default value as string
        personal_info['connections'] = int(connections_text.replace(
            'connections', '').replace('+', '').strip())

        personal_info.update(get_info(contact_info, {
            'email': '.ci-email .pv-contact-info__ci-container',
            'phone': '.ci-phone .pv-contact-info__ci-container > span:nth-child(1)',
            'connected': '.ci-connected .pv-contact-info__ci-container'
        }))

        vanity_url = text_or_default(
            contact_info, '.ci-vanity-url .pv-contact-info__ci-container', '').strip()
        # If none -> something broke getting the person's vanity url
        personal_info['url'] = normalize_url(
            vanity_url) if vanity_url != '' else None

        personal_info['websites'] = []
        if contact_info:
            websites = contact_info.select('.ci-websites li a')
            websites = list(map(lambda x: x['href'], websites))
            personal_info['websites'] = websites

        return personal_info

    @property
    def experiences(self):
        """
        Returns:
            dict of person's professional experiences.  These include:
                - Jobs
                - Education
                - Volunteer Experiences
                - Certifications
        """
        experiences = {}
        container = first_or_default(self.soup, '.background-section')

        jobs = all_or_default(
            container, '#experience-section ul .pv-position-entity')
        jobs = list(map(get_job_info, jobs))
        jobs = flatten_list(jobs)

        experiences['jobs'] = jobs

        schools = all_or_default(
            container, '#education-section ul .pv-education-entity')
        schools = list(map(get_school_info, schools))
        experiences['education'] = schools

        volunteering = all_or_default(
            container, '.pv-profile-section.volunteering-section .pv-volunteering-entity')
        volunteering = list(map(get_volunteer_info, volunteering))
        experiences['volunteering'] = volunteering

        certifications = all_or_default(
            container, '#certifications-section .pv-certification-entity')

        def parse_certifications(cerfification):
            """
            date_range contains no space in between but adds multiple spaces to the string
            This adds ` - ` in middle, splits all and joins with single space(' ')
            """
            certification_item = get_certifications_info(cerfification)
            date_range = certification_item["date_range"]

            if date_range is not None and 'Credential ID' not in date_range:
                date_range = ' '.join(date_range.replace('Expire', ' - Expire').replace(
                    'No Expiration', ' - No Expiration').split())
            else:
                date_range = 'Not Specified'

            return {
                'authority': certification_item['authority'] or 'Unknown',
                'title': certification_item['title'],
                'date_range': date_range
            }

        certifications = list(map(parse_certifications, certifications))
        experiences['certifications'] = certifications

        return experiences

    @property
    def skills(self):
        """
        Returns:
            list of skills {name: str, endorsements: int} in decreasing order of
            endorsement quantity.
        """
        skills_element = self.soup.select(
            '.pv-skill-category-entity__skill-wrapper')

        # this converts `endorsements` to integer value
        def parse_skills(skill):
            x = get_skill_info(skill)
            return {'name': normalize_string(x['name']), 'endorsements': int(x['endorsements'].replace('+', '').strip())}

        # calls `parse_skills()` with each item in `skills_element`
        skills = list(map(parse_skills, skills_element))

        # Sort skills based on endorsements
        return sorted(skills, key=lambda x: x['endorsements'], reverse=True)

    @property
    def accomplishments(self):
        """
        Returns:
            dict of professional accomplishments including:
                - publications
                - patents
                - courses
                - projects
                - honors
                - test scores
                - languages
                - organizations
        """
        # certifications doesn't go inside this div
        accomplishments = dict.fromkeys([
            'publications', 'patents',
            'courses', 'projects', 'honors',
            'languages', 'organizations'
        ])
        container = first_or_default(self.soup, '.pv-accomplishments-section')

        for key in accomplishments:
            accs = all_or_default(container, 'section.' + key + ' ul > li')
            accs = map(lambda acc: acc.get_text() if acc else None, accs)
            accomplishments[key] = list(accs)

        test_scores_element = all_or_default(
            container, 'section.test-scores ul > li')

        def parse_test_scores(test_score):
            x = get_test_score_info(test_score)
            return {'name': x['name'].replace('Test name\n', '').strip(), 'score': x['score']}

        # calls `parse_test_scores()` with each item in `test_scores_element`
        test_scores = list(map(parse_test_scores, test_scores_element))
        accomplishments['text_scores'] = test_scores

        return accomplishments

    @property
    def interests(self):
        """
        Returns:
            list of person's interests
        """
        container = first_or_default(self.soup, '.pv-interests-section')
        interests = all_or_default(container, 'ul > li')
        interests = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title'), interests)

        return list(interests)

    def to_dict(self):
        info = super(Profile, self).to_dict()
        info['personal_info']['current_company_link'] = ''
        jobs = info['experiences']['jobs']

        if jobs and jobs[0]['date_range'] and 'present' in jobs[0]['date_range'].lower():
            info['personal_info']['current_company_link'] = jobs[0]['li_company_url']
        else:
            print("Unable to determine current company...continuing")

        return info
