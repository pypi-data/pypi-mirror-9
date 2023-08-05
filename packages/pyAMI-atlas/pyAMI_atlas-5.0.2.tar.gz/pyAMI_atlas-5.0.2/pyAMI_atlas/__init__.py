# -*- coding: utf-8 -*-
from __future__ import (division, print_function, unicode_literals)
#############################################################################
# Author  : Jerome ODIER, Jerome FULACHIER, Fabian LAMBERT, Solveig ALBRAND
#
# Email   : jerome.odier@lpsc.in2p3.fr
#           jerome.fulachier@lpsc.in2p3.fr
#           fabian.lambert@lpsc.in2p3.fr
#           solveig.albrand@lpsc.in2p3.fr
#
# Version : 5.X.X (2014)
#
#############################################################################

import pyAMI.config, pyAMI_atlas.config

#############################################################################

pyAMI.config.version = pyAMI_atlas.config.version

pyAMI.config.bug_report = pyAMI_atlas.config.bug_report

#############################################################################

pyAMI.config.endpoints['atlas'] = {'prot': 'https', 'host': 'ami.in2p3.fr', 'port': '443', 'path': '/AMI/servlet/net.hep.atlas.Database.Bookkeeping.AMI.Servlet.FrontEnd'}
pyAMI.config.endpoints['atlas-replica'] = {'prot': 'https', 'host': 'atlas-ami.cern.ch', 'port': '443', 'path': '/AMI/servlet/net.hep.atlas.Database.Bookkeeping.AMI.Servlet.FrontEnd'}
pyAMI.config.endpoints['atlas-dev'] = {'prot': 'https', 'host': 'ccami025.in2p3.fr', 'port': '443', 'path': '/AMI/servlet/net.hep.atlas.Database.Bookkeeping.AMI.Servlet.FrontEnd'}

#############################################################################

pyAMI.config.tables['projects'] = {
	'tag': 'projectTag',
	'description': 'description',
	'is_base_type': 'isBaseType',
	'read_status': 'readStatus=VALID',
	'write_status': 'writeStatus',
	'manager': 'projectManager',

	'@entity': 'projects',
	'@project': 'Atlas_Production',
	'@processing_step': '*',

	'@primary': 'tag',
	'@foreign': 'nomenclature',
}

pyAMI.config.tables['subprojects'] = {
	'tag': 'subProjectTag',
	'description': 'description',
	'is_base_type': 'isBaseType',
	'read_status': 'readStatus=VALID',
	'write_status': 'writeStatus',
	'manager': 'projectManager',

	'@entity': 'subprojects',
	'@project': 'Atlas_Production',
	'@processing_step': '*',

	'@primary': 'tag',
}

pyAMI.config.tables['types'] = {
	'name': 'dataType',
	'description': 'description',
	'read_status': 'readStatus=VALID',
	'write_status': 'writeStatus',

	'@entity': 'data_type',
	'@project': 'Atlas_Production',
	'@processing_step': '*',

	'@primary': 'name',
}

pyAMI.config.tables['subtypes'] = {
	'name': 'subDataType',
	'description': 'description',
	'read_status': 'readStatus=VALID',
	'write_status': 'writeStatus',

	'@entity': 'subData_type',
	'@project': 'Atlas_Production',
	'@processing_step': '*',

	'@primary': 'name',
}

pyAMI.config.tables['prodsteps'] = {
	'tag': 'productionStepTag',
	'name': 'productionStepName',
	'read_status': 'readStatus=VALID',
	'write_status': 'writeStatus',

	'@entity': 'productionStep',
	'@project': 'Atlas_Production',
	'@processing_step': '*',

	'@primary': 'tag, name',
}

pyAMI.config.tables['nomenclature'] = {
	'tag': 'nomenclatureTag',
	'template': 'nomenclatureTemplate',
	'description': 'nomenclatureName',
	'read_status': 'readStatus=VALID',
	'write_status': 'writeStatus',

	'@entity': 'nomenclature',
	'@project': 'Atlas_Production',
	'@processing_step': '*',

	'@primary': 'tag, template, description',
}

pyAMI.config.tables['datasets'] = {
	'ami_status': 'amiStatus=VALID',
	'atlas_release': 'AtlasRelease',
	'beam': 'beamType',
	'conditions_tag': 'conditionsTag',
	'cross_section': 'crossSection',
	'data_period': 'period',
	'dataset_number': 'datasetNumber',
	'ecm_energy': 'ecmEnergy',
	'events': 'totalEvents',
	'generator_name': 'generatorName',
	'generator_tune': 'generatorTune',
	'geometry': 'geometryVersion',
	'in_container': 'inContainer',
	'job_config': 'jobConfig',
	'ldn': 'logicalDatasetName',
	'modified': 'lastModified',
	'nfiles': 'nFiles',
	'pdf': 'PDF',
	'physics_comment': 'physicsComment',
	'physics_short': 'physicsShort',
	'production_step': 'productionStep',
	'prodsys_status': 'prodsysStatus',
	'project': 'projectName',
	'requested_by': 'requestedBy',
	'responsible': 'physicistResponsible',
	'run_number': 'runNumber',
	'stream': 'streamName',
	'total_size': 'totalSize',
	'transformation_package': 'TransformationPackage',
	'trash_annotation': 'trashAnnotation',
	'trash_date': 'trashDate',
	'trash_trigger': 'trashTrigger',
	'trigger_config': 'triggerConfig',
	'type': 'dataType',
	'version': 'version',

	'@entity': 'dataset',
	'@project': 'Atlas_Production',
	'@processing_step': 'Atlas_Production',

	'@primary': 'ldn',
	'@foreign': 'files',
}

pyAMI.config.tables['files'] = {
	'lfn': 'LFN',
	'guid': 'fileGUID',
	'size': 'fileSize',
	'events': 'events',
	'input_file': 'inputFile',
	'gen_filt_eff': 'GenFiltEff',
	'cross_section': 'crossSection',

	'@entity': 'files',
	'@project': 'Atlas_Production',
	'@processing_step': 'Atlas_Production',

	'@primary': 'lfn',
}

#############################################################################
