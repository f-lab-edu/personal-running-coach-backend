from .auth.auth import router as authR
from .profile import router as profileR
from .statistics import router as statsR
from .training import router as trainingR



routers = [authR, profileR, statsR, trainingR]