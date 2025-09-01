from .auth.auth import router as authR
from .profile import router as profileR
from .statistics import router as statsR
from .trainSession import router as trainsessionR



routers = [authR, profileR, statsR, trainsessionR]