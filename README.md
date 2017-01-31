This is a test package for me to test out the JT51 quickly. MiSoC is
most likely complete overkill for a sound CPU. At the moment, this only
supports the minispartan6. If you do not have a minispartan6, check out
`build/sim` for a Makefile for a simulation (make sure to supply your own
`path.mak`). The Makefile requires an LatticeMico32 toolchain, and your usual
host of POSIX utilities (including `m4` to generate a header file of useful
constants).

Because of the `__main__.py`, this package should be run directly instead
of installing. Try the following command for a simulated environment:

```
PYTHONPATH=$(YMSOC) python3 -m ymsoc --device xc6slx25 build --jt51-dir $(JT51) --output-dir $(YMSOC)/build --no-compile-gateware ymsoc.platforms.sim
```
