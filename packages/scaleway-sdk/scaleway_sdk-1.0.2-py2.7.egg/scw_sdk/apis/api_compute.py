# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014 Online SAS and Contributors. All Rights Reserved.
#                         Julien Castets <jcastets@scaleway.com>
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause

from . import API


class ComputeAPI(API):

    base_url = 'https://api.scaleway.com/'
