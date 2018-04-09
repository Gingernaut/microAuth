import hug


@hug.post('/accountreset')
def get_acc(emailAddr):
    return "account"
