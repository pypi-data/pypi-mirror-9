from .ui import q, play

def example():
    import sys
    for tongue_twister in play():
        args = (tongue_twister['translation'],
                tongue_twister['language'],
                tongue_twister['original'])
        sys.stdout.write('%s\n(%s: %s)\n\n' % args)
