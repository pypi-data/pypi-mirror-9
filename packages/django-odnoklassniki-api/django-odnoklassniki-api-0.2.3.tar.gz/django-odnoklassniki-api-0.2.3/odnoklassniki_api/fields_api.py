# -*- coding: utf-8 -*-
'''
List of fields from API docs
http://apiok.ru/wiki/display/api/fields
'''

API_REQUEST_FIELDS = {
    'media_topic': [
        'author_ref',
        'created_ms',
        'id',
        'like_summary',
        'media',
        'media_description',
        'media_movie_refs',
        'media_music_track_refs',
        'media_photo_refs',
        'media_reshare',
        'media_text',
        'media_title',
        'media_type',
        'media_url',
    ],
    'feed': [
        'type',
        'date',
        'feed_owner_refs',
        'message',
        'group',
        'actor_refs',
        'mark_as_spam_id',
        'like_summary',
        'photo_main',
        'photo_refs',
        'album_refs',
        'owner_refs',
        'friend_refs',
        'target_refs',
        'post_status',
        'post_refs',
        'present_refs',
        'sender_refs',
        'receiver_refs',
    ],
    'group_album': [
        'aid',
        'author_name',
        'author_type',
        'created',
        'group_id',
        # Next one yeild 'attrs' attribute in OK server response.
        'like_allowed',
        'like_summary',
        'photos_count',
        # Next one present in docs still its meaning is unknown
        'ref',
        'title',
        'user_id',
        # Next 3 are documented. Still yeild no results for group album
        'modify_allowed',
        'delete_allowed',
        'add_photo_allowed',
    ],
    'group_photo': [
        'album_id',
        'author_name',
        'author_type',
        'comments_count',
        'created_ms',
        'discussion_summary',
        'group_id',
        'id',
        'like_count',
        'like_summary',
        # Undocumented alas retuned in resp to group_photo.*
        'liked_it',
        # Next 2 yeild 'attrs' attribute in OK server response.
        'like_allowed',
        'mark_as_spam_allowed',
        # Next one is undocumented. Returned in response to fields: group_photo.*
        'pic1024max',
        'pic1024x768',
        'pic128max',
        'pic128x128',
        'pic180min',
        # Next one present in docs. Still yeilds no results for group photos.getPhotos
        'pic190x190',
        'pic240min',
        'pic320min',
        'pic50x50',
        'pic640x480',
        'standard_height',
        'standard_width',
        'text',
    ],
    'discussion': [
        'object_type',
        'object_id',
        'title',
        'truncated',
        'message',
        'access_restricted',
        'creation_date',
        'last_activity_date',
        'last_user_access_date',
        'new_comments_count',
        'total_comments_count',
        'owner_uid',
        'like_summary',
        'like_allowed',
        'mark_as_spam_allowed',
        'comment_allowed',
        'comment_as_admin_allowed',
        'subscribe_allowed',
        'unsubscribe_allowed',
        'likes_unread',
        'reply_unread',
    ],
    'group': [
        'uid',
        'ref',
        'name',
        'description',
        'shortname',
        'pic_avatar',
        'photo_id',
        'shop_visible_admin',
        'shop_visible_public',
        'add_photoalbum_allowed',
        'change_avatar_allowed',
        'members_count',
        'premium',
        'private',
    ],
    'user': [
        'uid',
        'locale', #(en, lv, ... [language[_territory][.codeset][@modifier]] )
        'first_name',
        'last_name',
        'name',
        'gender',
        'age',
        'birthday', #(yyyy-MM-dd)
        'has_email',
        'location',
        'current_location',
        'current_status', # (текст статуса)
        'current_status_id', # (уникальный идентификатор статуса)
        'current_status_date', # (дата создания статуса)
        'online',
        'last_online',
        'photo_id', # - id главной фотографии
#         'pic_1', # - то же что и pic50x50
#         'pic_2', # - то же что и pic128max
#         'pic_3', # - то же что и pic190x190
#         'pic_4', # - то же что и pic640x480
#         'pic_5', # - то же что и pic128x128
        'pic50x50', # - квадратная аватарка 50x50
        'pic128x128', # - квадратная аватарка 128x128
        'pic128max', # - аватарка, вписанная в квадрат 128x128
        'pic180min', # - аватарка, заресайзенная по минимальной стороне 180
        'pic240min', # - аватарка, заресайзенная по минимальной стороне 240
        'pic320min', # - аватарка, заресайзенная по минимальной стороне 320
        'pic190x190', # - квадратная аватарка 190x190
        'pic640x480', # - аватарка, вписанная в квадрат 640x480
        'pic1024x768', # - аватарка, вписанная в квадрат 1024x768
        'url_profile',
        'url_chat',
        'url_profile_mobile',
        'url_chat_mobile',
        'can_vcall',
        'can_vmail',
#        'email', # GET_EMAIL permission is required
        'allows_anonym_access',
        'allows_messaging_only_for_friends',
        'registered_date',
        'has_service_invisible',
    ],
    'comment': [
        'id',
        'author_id',
        'author_type',
        'author_name',
        'text',
        'date',
        'type',
        'reply_to_comment_id',
        'reply_to_id',
        'reply_to_type',
        'reply_to_name',
        'like_summary',
        'delete_allowed',
        'like_allowed',
        'mark_as_spam_allowed',
        'author_block_allowed',
        'likes_unread',
        'reply_unread',
    ]
}