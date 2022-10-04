/*
 * Author:   Niels Nuyttens  <niels@nannyml.com>
 *
 * License: Apache Software License 2.0
 */

CREATE DATABASE nannyml;
CREATE USER nannyml WITH ENCRYPTED PASSWORD 'we<3nannyml';
GRANT ALL PRIVILEGES ON DATABASE nannyml TO nannyml;
