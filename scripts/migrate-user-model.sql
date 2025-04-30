INSERT INTO django_migrations (app, name, applied) VALUES ('accounts', '0001_initial', CURRENT_TIMESTAMP);
UPDATE django_content_type SET app_label = 'accounts' WHERE app_label = 'auth' and model = 'user';
