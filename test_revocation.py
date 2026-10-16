from consent import revoke_consent

success = revoke_consent("Krishna", "hospital_a")

if success:
    print("Consent revoked successfully!")
else:
    print("Consent record not found.")