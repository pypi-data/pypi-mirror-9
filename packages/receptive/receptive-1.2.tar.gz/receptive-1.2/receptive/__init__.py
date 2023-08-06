import hashlib

def extract_vals(d, accum):
    for key, value in d.iteritems():
        if isinstance(value, dict):
            extract_vals(value, accum)
        else:
            accum.append(value)                

def sign(unsigned, secret):
    vals = [secret]
    extract_vals(unsigned, vals)
    vals.sort()
    unsigned['signature'] = hashlib.sha256(','.join(vals)).hexdigest()
    return unsigned

