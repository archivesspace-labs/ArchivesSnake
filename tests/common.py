from vcr import VCR

vcr = VCR(func_path_generator = lambda test: "tests/fixtures/cassettes/{}--{}.yaml".format(test.__module__, test.__name__))
