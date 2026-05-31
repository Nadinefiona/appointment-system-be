# Line 1 = endpoint title (Swagger list). Line 2 = access (visible before expand).


def endpoint(title, access):
    return f"{title}\n{access}"


REGISTER = endpoint("Register client", "Access: public")
LOGIN = endpoint("Login", "Access: public")
REFRESH = endpoint("Refresh token", "Access: public")

ME_GET = endpoint("My profile", "Access: client, provider, admin")
ME_PATCH = endpoint("Update profile", "Access: client, provider, admin")

PROVIDERS_LIST = endpoint("List providers", "Access: read all · write admin")
PROVIDERS_GET = endpoint("Get provider", "Access: read all · write admin")
PROVIDERS_CREATE = endpoint("Create provider", "Access: admin")
PROVIDERS_UPDATE = endpoint("Update provider", "Access: admin")
PROVIDERS_PATCH = endpoint("Patch provider", "Access: admin")
PROVIDERS_DELETE = endpoint("Delete provider", "Access: admin")
PROVIDERS_SCHEDULE = endpoint("Schedule", "Access: provider own · admin")
PROVIDERS_OPENINGS = endpoint("Openings", "Access: client, provider, admin")

SERVICES_LIST = endpoint("List services", "Access: read all · write admin")
SERVICES_GET = endpoint("Get service", "Access: read all · write admin")
SERVICES_CREATE = endpoint("Create service", "Access: admin · name + providers[]")
SERVICES_UPDATE = endpoint("Update service", "Access: admin")
SERVICES_PATCH = endpoint("Patch service", "Access: admin")
SERVICES_DELETE = endpoint("Delete service", "Access: admin")

AVAIL_LIST = endpoint("List slots", "Access: provider own · admin")
AVAIL_GET = endpoint("Get slot", "Access: provider own · admin")
AVAIL_CREATE = endpoint("Create slot", "Access: provider only · send weekday, start_time, end_time")
AVAIL_UPDATE = endpoint("Update slot", "Access: provider own · admin · no overlap")
AVAIL_PATCH = endpoint("Edit slot", "Access: provider own · admin · PATCH weekday/times")
AVAIL_DELETE = endpoint("Delete slot", "Access: provider own · admin")

BOOKINGS_LIST = endpoint("List bookings", "Access: client own · provider · admin")
BOOKINGS_GET = endpoint("Get booking", "Access: client own · provider · admin")
BOOKINGS_CREATE = endpoint("Create booking", "Access: client · start_time + note only")
ADMIN_USER_LIST = endpoint("List users", "Access: admin")
ADMIN_USER_ROLE = endpoint("Change user role", "Access: admin · PATCH role only")
BOOKINGS_CANCEL = endpoint("Cancel booking", "Access: client own · provider · admin")
