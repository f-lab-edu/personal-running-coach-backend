from .auth.auth import router as authR
from .profile import router as profileR
from .ai import router as aiR
from .train_session import router as trainsessionR



routers = [authR, profileR, aiR, trainsessionR]