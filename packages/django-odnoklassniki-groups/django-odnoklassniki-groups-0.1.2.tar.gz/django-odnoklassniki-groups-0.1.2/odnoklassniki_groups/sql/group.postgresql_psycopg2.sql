--odnoklassniki_groups_group_users

CREATE UNIQUE INDEX odnoklassniki_groups_group_users_time_from_3col_uniq
ON odnoklassniki_groups_group_users (group_id, user_id, time_from)
WHERE time_from IS NOT NULL;

CREATE UNIQUE INDEX odnoklassniki_groups_group_users_time_from_2col_uniq
ON odnoklassniki_groups_group_users (group_id, user_id)
WHERE time_from IS NULL;

CREATE UNIQUE INDEX odnoklassniki_groups_group_users_time_to_3col_uniq
ON odnoklassniki_groups_group_users (group_id, user_id, time_to)
WHERE time_to IS NOT NULL;

CREATE UNIQUE INDEX odnoklassniki_groups_group_users_time_to_2col_uniq
ON odnoklassniki_groups_group_users (group_id, user_id)
WHERE time_to IS NULL;