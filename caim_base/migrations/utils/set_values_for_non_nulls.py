
AGE_TEMP_DEFAULT = 0
NUM_OF_PEOPLE_IN_HOME_DEFAULT = 0
REFERENCE_1_DEFAULT = "REFERENCE_1 N/A"
REFERENCE_2_DEFAULT = "REFERENCE_2 N/A"
REFERENCE_3_DEFAULT = "REFERENCE_3 N/A"


def set_values_for_non_nulls(apps, schema_editor):
    FostererProfile = apps.get_model('caim_base', 'fostererprofile')
    FostererProfile.objects.filter(age=None).update(age=AGE_TEMP_DEFAULT)
    FostererProfile.objects.filter(num_people_in_home=None).update(num_people_in_home=AGE_TEMP_DEFAULT)
    FostererProfile.objects.filter(reference_1=None).update(reference_1=REFERENCE_1_DEFAULT)
    FostererProfile.objects.filter(reference_2=None).update(reference_2=REFERENCE_2_DEFAULT)
    FostererProfile.objects.filter(reference_3=None).update(reference_3=REFERENCE_3_DEFAULT)


def reverse_set_values_for_non_nulls(apps, schema_editor):
    FostererProfile = apps.get_model('caim_base', 'fostererprofile')
    FostererProfile.objects.filter(age=AGE_TEMP_DEFAULT).update(age=None)
    FostererProfile.objects.filter(num_people_in_home=AGE_TEMP_DEFAULT).update(num_people_in_home=None)
    FostererProfile.objects.filter(reference_1=REFERENCE_1_DEFAULT).update(reference_1=None)
    FostererProfile.objects.filter(reference_2=REFERENCE_2_DEFAULT).update(reference_2=None)
    FostererProfile.objects.filter(reference_3=REFERENCE_3_DEFAULT).update(reference_3=None)
