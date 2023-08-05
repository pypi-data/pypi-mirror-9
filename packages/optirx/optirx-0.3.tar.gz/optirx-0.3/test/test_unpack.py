from __future__ import print_function
from nose.tools import assert_equal, assert_in, assert_is


def assert_almost_equal(actual, expected, decimal=7, ctx=None):
    if hasattr(actual, "__iter__"):
        for a, e in zip(actual, expected):
            try:
                assert_almost_equal(a, e, decimal=decimal)
            except AssertionError as e:
                newmsg = "\n".join(["sequences are not almost equal:",
                                    "  actual:   " + str(actual),
                                    "  expected: " + str(expected),
                                    "because inner " + e.message])
                raise AssertionError(newmsg)

    else:
        diff = abs(actual - expected)
        maxdiff = 0.5 * 10**(-decimal)
        msg = "\n".join(["items are not almost equal up to %.e" % maxdiff,
                         "  actual:     " + str(actual),
                         "  expected:   " + str(expected),
                         "  difference: %.1e" % (diff)])
        assert diff < maxdiff, msg


import optirx as rx


def test_unpack_sender_data_all_versions():
    files = ["test/data/frame-motive-1.5.0-000.bin",
             "test/data/frame-motive-1.7.2-000.bin"]
    versions = [(2,5,0,0), (2,7,0,0)]

    for fname, version in zip(files, versions):
        with open(fname, "rb") as f:
            binary = f.read()
            parsed = rx.unpack(binary)
            expected = rx.SenderData(appname=b"NatNetLib",
                                     version=version,
                                     natnet_version=version)
            print("parsed:\n",parsed)
            print("expected:\n",expected)
            assert_equal(parsed, expected)


def test_unpack_frame_of_data_natnet2500():

    expected_rb = [
        (-0.3015673756599426, 0.08478303998708725, 1.1143304109573364),
        (-0.23079043626785278, 0.04755447059869766, 1.1353150606155396),
        (-0.25711703300476074, -0.014958729967474937, 1.1209092140197754)]

    expected_om = [
        (-0.24560749530792236, 0.1687806248664856, 1.2753326892852783),
        (-0.11109362542629242, 0.1273186355829239, 1.2400494813919067)]

    for i in range(1,1+2):
        with open("test/data/frame-motive-1.5.0-%03d.bin" % i, "rb") as f:
            binary = f.read()
            parsed = rx.unpack(binary)
            assert_is(type(parsed), rx.FrameOfData)
            assert_in(parsed.frameno, [92881, 92882])
            assert_in(b"all", parsed.sets)
            assert_in(b"Rigid Body 1", parsed.sets)
            assert_almost_equal(parsed.sets[b"Rigid Body 1"], expected_rb, 4)
            assert_equal(parsed.rigid_bodies[0].mrk_ids, (1,2,3))
            assert_equal(len(parsed.other_markers), 2)
            assert_almost_equal(parsed.other_markers, expected_om, 3)
            assert_equal(parsed.skeletons, [])
            assert_equal(len(parsed.labeled_markers), 3)


def test_unpack_frame_of_data_natnet2700():

    expected_rb = [
        (-0.053690, 0.099419, -1.398518),
        ( 0.047905, 0.115714, -1.436263),
        ( 0.023839, 0.072290, -1.388070)]

    expected_om = [
        (-0.254053, 0.055445, -1.432309),
        (-0.281266, 0.049510, -1.421349)]

    for i in range(1,1+2):
        with open("test/data/frame-motive-1.7.2-%03d.bin" % i, "rb") as f:
            binary = f.read()
            parsed = rx.unpack(binary, (2,7,0,0))
            print(parsed)
            assert_is(type(parsed), rx.FrameOfData)
            assert_in(parsed.frameno, [411213, 411214, 411215])
            assert_in(b"all", parsed.sets)
            assert_in(b"Rigid Body 1", parsed.sets)
            assert_almost_equal(parsed.sets[b"Rigid Body 1"], expected_rb, 4)
            assert_equal(parsed.rigid_bodies[0].mrk_ids, (1,2,3))
            assert_equal(len(parsed.other_markers), 2)
            assert_almost_equal(parsed.other_markers, expected_om, 3)
            assert_equal(parsed.skeletons, [])
            assert_equal(len(parsed.labeled_markers), 3)

