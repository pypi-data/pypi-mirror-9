from juju_scaleway.exceptions import ConstraintError


SERIES_MAP = {
    'Ubuntu Utopic (14.10)': 'utopic',
    'Ubuntu Trusty (14.04 LTS)': 'trusty',
}


def get_images(client):
    images = {}
    for i in client.get_images():
        if not i.public:
            continue

        for s in SERIES_MAP:
            if ("%s" % s) == i.name:
                images[SERIES_MAP[s]] = i.id
    return images
