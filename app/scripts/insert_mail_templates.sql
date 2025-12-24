-- Insert default mail templates

-- Welcome email template
INSERT INTO mail_templates (key, subject, body, created_at, updated_at)
VALUES (
    'welcome',
    'Welcome to The Church Manager',
    'Hello {{first_name}} {{last_name}},\n\nWelcome to The Church Manager! We are excited to have you join our community.\n\nYour account has been successfully created. You can now access all the features and services we offer.\n\nIf you have any questions, please feel free to contact us.\n\nBest regards,\nThe Church Manager Team',
    NOW(),
    NOW()
)
ON CONFLICT (key) DO NOTHING;

-- Forgot password email template
INSERT INTO mail_templates (key, subject, body, created_at, updated_at)
VALUES (
    'forgot_password',
    'Password Reset Request - The Church Manager',
    'Hello {{first_name}} {{last_name}},\n\nWe received a request to reset your password for your account.\n\nIf you requested this password reset, please click on the following link to reset your password:\n{{reset_link}}\n\nThis link will expire in {{expiry_time}}.\n\nIf you did not request a password reset, please ignore this email. Your password will remain unchanged.\n\nFor security reasons, please do not share this link with anyone.\n\nBest regards,\nThe Church Manager Team',
    NOW(),
    NOW()
)
ON CONFLICT (key) DO NOTHING;

-- User created by organization email template
INSERT INTO mail_templates (key, subject, body, created_at, updated_at)
VALUES (
    'user_created_by_organization',
    'Welcome to The Church Manager - Account Created',
    'Hello {{first_name}} {{last_name}},\n\nYour account has been created by {{organization_name}} on The Church Manager platform.\n\nYour login credentials:\nEmail: {{email}}\nPhone: {{phone}}\n\nTo proceed and set your password, please click on the following link to reset your password:\n{{reset_link}}\n\nThis link will redirect you to the forgot password page where you can set your password.\n\nIf you have any questions, please contact your organization administrator.\n\nBest regards,\nThe Church Manager Team',
    NOW(),
    NOW()
)
ON CONFLICT (key) DO NOTHING;

