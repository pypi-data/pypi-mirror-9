from numpy.testing import assert_equal
from gatspy.datasets import RRLyraeGenerated, fetch_rrlyrae

rrlyrae = fetch_rrlyrae()
lcid = rrlyrae.ids[100]

gen = RRLyraeGenerated(lcid)

t, y, dy = gen.observed('g')
y = gen.generated('g', t, dy)
