from datetime import datetime
from pathlib import Path
import json


def log_to_file(scraped_data):
    # write response to file
    try:
        base_path = Path(__file__).parent
        # in `user-johndoe-14-06-2020-12-33-22` format
        filename = 'user-{0}-{1}.json'.format(scraped_data["personal_info"]["url"].replace(
            '/in/', '').replace('/', ''), datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
        logs_path = '../../logs/{}'.format(filename)
        file_path = (base_path / logs_path).resolve()

        with open(file_path, 'w', encoding='utf-8') as f:
            # print("Writing response to file...")
            json.dump(scraped_data, f, ensure_ascii=False,
                      sort_keys=True, indent=4)
            # print("Success! File created")
    except Exception as err:
        print(err)
        print("Error: Writing response to file failed")


def get_cloudinary_user_folder(url):
    return 'epimatch/users/user-{0}'.format(url.replace('/in/', '').replace('/', ''))
