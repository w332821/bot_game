import bcrypt

# The stored hash from database
stored_hash = '$2a$10$3zjq1DfSixKeuMYlAWsNKOz1xj/KpVU9euFQVNm1K192XkOqYSaDG'

# Try common passwords
test_passwords = ['admin', 'Admin', 'admin123', '123456', 'password', 'Admin123']

print("Testing passwords against stored hash:")
print(f"Stored hash: {stored_hash}\n")

for pwd in test_passwords:
    try:
        result = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"Password '{pwd}': {'✓ MATCH' if result else '✗ No match'}")
    except Exception as e:
        print(f"Password '{pwd}': Error - {e}")
