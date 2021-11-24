# revimboard - A ReviewBoard client for VIM
#
# Copyright 2021 Ben Jackson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# https://www.reviewboard.org/docs/manual/dev/webapi/2.0/errors/
DOES_NOT_EXIST                                       = 100
PERMISSION_DENIED                                    = 101
INVALID_ATTRIBUTE                                    = 102
NOT_LOGGED_IN                                        = 103
LOGIN_FAILED                                         = 104
INVALID_FORM_DATA                                    = 105
MISSING_ATTRIBUTE                                    = 106
ENABLE_EXTENSION_FAILED                              = 107
DISABLE_EXTENSION_FAILED                             = 108
EXTENSION_ALREADY_INSTALLED                          = 109
INSTALL_EXTENSION_FAILED                             = 110
DUPLICATE_ITEM                                       = 111
OAUTH2_MISSING_SCOPE_ERROR                           = 112
OAUTH2_ACCESS_DENIED_ERROR                           = 113
RATE_LIMIT_EXCEEDED                                  = 114
INVALID_CHANGE_NUMBER                                = 203
CHANGE_NUMBER_IN_USE                                 = 204
MISSING_REPOSITORY                                   = 205
INVALID_REPOSITORY                                   = 206
REPOSITORY_FILE_NOT_FOUND                            = 207
INVALID_USER                                         = 208
REPOSITORY_ACTION_NOT_SUPPORTED                      = 209
REPOSITORY_INFORMATION_ERROR                         = 210
EMPTY_CHANGESET                                      = 212
SERVER_CONFIGURATION_ERROR                           = 213
BAD_HOST_KEY                                         = 214
UNVERIFIED_HOST_KEY                                  = 215
UNVERIFIED_HOST_CERTIFICATE                          = 216
MISSING_USER_KEY                                     = 217
REPOSITORY_AUTHENTICATION_ERROR                      = 218
DIFF_EMPTY                                           = 219
DIFF_TOO_BIG                                         = 220
FILE_RETRIEVAL_ERROR                                 = 221
HOSTING_SERVICE_AUTHENTICATION_ERROR                 = 222
GROUP_ALREADY_EXISTS                                 = 223
DIFF_PARSE_ERROR                                     = 224
PUBLISH_ERROR                                        = 225
USER_QUERY_ERROR                                     = 226
COMMIT_ID_ALREADY_EXISTS                             = 227
TOKEN_GENERATION_FAILED                              = 228
COULD_NOT_CLOSE_REVIEW_REQUEST                       = 230
COULD_NOT_REOPEN_REVIEW_REQUEST                      = 231
SHIPIT_REVOCATION_ERROR                              = 232
