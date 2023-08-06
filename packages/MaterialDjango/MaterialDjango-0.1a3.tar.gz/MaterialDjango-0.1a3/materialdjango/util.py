from django.template.loader import get_template
from django.template import Context, Template

def vulcanize_prep(templatename):
    "make html!"
    return get_template(templatename).render(Context())

if __name__ == '__main__':
    import sys
    print vulcanize_prep(sys.argv[1])