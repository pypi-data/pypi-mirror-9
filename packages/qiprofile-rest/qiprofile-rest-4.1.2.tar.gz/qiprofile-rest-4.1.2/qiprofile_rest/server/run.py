#!/usr/bin/env python
import importlib
import mongoengine
from eve import Eve
from eve_mongoengine import EveMongoengine
from qiprofile_rest.model.subject import Subject
from qiprofile_rest.model.imaging import (SessionDetail, Scan, ScanProtocol,
                                          RegistrationProtocol,
                                          ModelingProtocol)

# The application. 
app = Eve()

# The MongoEngine ORM extension.
ext = EveMongoengine(app)

# Register the model non-embedded documdent classes.
ext.add_model(Subject, url='subject')
ext.add_model(SessionDetail, url='session-detail')
ext.add_model(ScanProtocol, url='scan-protocol')
ext.add_model(RegistrationProtocol, url='registration-protocol')
ext.add_model(ModelingProtocol, url='modeling-protocol')


if __name__ == '__main__':
    app.run()
