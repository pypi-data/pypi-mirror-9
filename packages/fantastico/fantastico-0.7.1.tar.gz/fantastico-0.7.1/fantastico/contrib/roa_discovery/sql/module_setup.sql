##############################################################################################################################
# Copyright 2013 Cosnita Radu Viorel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##############################################################################################################################

##############################################################################################################################
#
# This script is used to create sample resource required tables.
#
##############################################################################################################################

CREATE TABLE IF NOT EXISTS sample_resources(
	id INTEGER AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	total FLOAT NOT NULL,
	vat FLOAT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS sample_resource_subresources(
	id INTEGER AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	resource_id INTEGER NOT NULL,
	PRIMARY KEY(id),
	CONSTRAINT fk_sample_subresources_resource FOREIGN KEY(resource_id) REFERENCES sample_resources(id)
);