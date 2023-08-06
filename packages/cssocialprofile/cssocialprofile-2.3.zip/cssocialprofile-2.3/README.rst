================
CS SOCIALPROFILE
================

Based on `django-socialprofile <https://github.com/cyface/django-socialprofile>`_ and adapted by `Code Syntax <https://www.codesyntax.com>`_

CONFIGURATION
=============

Just write this in your settings.py file:


  SOCIAL_AUTH_PIPELINE = (
      'social_auth.backends.pipeline.social.social_auth_user',
      'social_auth.backends.pipeline.associate.associate_by_email',
      'social_auth.backends.pipeline.user.get_username',
      'social_auth.backends.pipeline.user.create_user',
      'social_auth.backends.pipeline.social.associate_user',
      'social_auth.backends.pipeline.user.update_user_details',
      'social_auth.backends.pipeline.social.load_extra_data',
      'cssocialprofile.pipeline.extra_values.twitter_extra_values',
      'cssocialprofile.pipeline.extra_values.facebook_extra_values',
      'cssocialprofile.pipeline.extra_values.openid_extra_values',
  )
