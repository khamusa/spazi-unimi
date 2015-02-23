# Spazi Unimi
Spazi Unimi is a project developed in coordination with Collegio Didattico Dipartimentale di Informatica - CCDINF of Università degli Studi di Milano (Milan), by Samuel Brandão, Diego Costantino and Paolo Venturi, as a Bachelors Degree final project, under coordination of Associate Professor PhD Carlo Bellettini.

The project aims at obtaining architectonic data from different University departments, performing its validation and sanitation in order to be able to comprehend it and finally supply an useful API for future use. In particular the project previews the development of an Android Application as a demonstration of the potentiality of this kind of information, specially in association with Geolocation technologies.

This repository contains part of the backend system, specially the functionalities used for processing, filtering and merging data from the different sources. A particular effort has been put into filtering, comparing and validating the inputs, performing the often difficult task of detecting and correcting unpredictable human errors.

The system currently works on the processing of DXF files (Drawing Exchange Format, a CAD compatible format) to obtain buildings/floors information and tabular data supplied by different departments (as csv, json or xml formats). The acquired data is then processed, compared and decisions are taken on how to merge them into a single data source.
