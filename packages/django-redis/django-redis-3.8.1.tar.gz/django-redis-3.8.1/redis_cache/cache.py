from django_redis.cache import *
import warnings
warnings.warn("The 'redis_cache' package name is deprecated. Please rename it "
              "for 'django_redis'.", DeprecationWarning)
