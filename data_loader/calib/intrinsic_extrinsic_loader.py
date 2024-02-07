#!/usr/bin/python3

import os
import sys
import numpy as np
import yaml

sys.path.append('tools')
import eigen_conversion 

sys.path.append('sensor')
from camera_pinhole import CameraPinhole
from lidar import Lidar

# sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

class IntrinsicExtrinsicLoader():
	def __init__(self, is_print=False):
		self.is_print = is_print
		self.sensor_collection = {}
		self.extrinsics_collection = {}

	def load_calibration(self, calib_path, sensor_frameid_dict):
		# Initialize sensor extrinsics object
		self.extrinsics_collection = {} # extrinsics_collection['ouster00']
		for sensor, value in sensor_frameid_dict.items():
			frame_id = value[0]
			self.extrinsics_collection[frame_id] = {}

		# Initialize sensor collection object
		self.sensor_collection = {} # sensor_collection['ouster']
		for sensor, value in sensor_frameid_dict.items():
			frame_id = value[0]
			yaml_path = os.path.join(calib_path, frame_id + '.yaml')
			print('Loading Intrinsic Extrinsics from {:<20} ...'.format(yaml_path))
			if 'ouster' in sensor:
				self.load_lidar(sensor, frame_id, yaml_path)
			elif 'frame' in sensor:
				self.load_frame_camera(sensor, frame_id, yaml_path)
			elif ('event' in sensor) and ('camera' in sensor):
				self.load_event_camera(sensor, frame_id, yaml_path)
			else:
				print('Unknown sensor: {:<20}'.format(sensor))
		
		if self.is_print:
			print('Sensors:')
			print(self.sensor_collection)
			print('Extrinsics:')
			print(self.extrinsics_collection)
			
	def load_lidar(self, sensor, frame_id, yaml_path):
		with open(yaml_path, 'r') as yaml_file:
			yaml_data = yaml.safe_load(yaml_file)

			if 'sensor_frame_cam00' in yaml_data:
				translation = np.array(yaml_data['translation_sensor_frame_cam00']['data'])
				quaternion = np.array(yaml_data['quaternion_sensor_frame_cam00']['data'])
				T_sensor_framecam00 = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])
				self.extrinsics_collection[frame_id]['frame_cam00'] = T_sensor_framecam00
				self.extrinsics_collection['frame_cam00'][frame_id] = np.linalg.inv(T_sensor_framecam00)

			if 'sensor_vehicle_frame_cam00' in yaml_data:
				translation = np.array(yaml_data['translation_sensor_vehicle_frame_cam00']['data'])
				quaternion = np.array(yaml_data['quaternion_sensor_vehicle_frame_cam00']['data'])
				T_sensor_framecam00 = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])
				self.extrinsics_collection[frame_id]['vehicle_frame_cam00'] = T_sensor_framecam00
				self.extrinsics_collection['vehicle_frame_cam00'][frame_id] = np.linalg.inv(T_sensor_framecam00)

			if 'sensor_event_cam00' in yaml_data:
				translation = np.array(yaml_data['translation_sensor_event_cam00']['data'])
				quaternion = np.array(yaml_data['quaternion_sensor_event_cam00']['data'])
				T_sensor_eventcam00 = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])
				self.extrinsics_collection[frame_id]['event_cam00'] = T_sensor_eventcam00
				self.extrinsics_collection['event_cam00'][frame_id] = np.linalg.inv(T_sensor_eventcam00)   
				
			lidar = Lidar()
			if self.is_print:
				print(lidar)
			self.sensor_collection[sensor] = lidar

	# NOTE(gogojjh): can only handle pinhole camera
	def load_frame_camera(self, sensor, frame_id, yaml_path):
		with open(yaml_path, 'r') as yaml_file:
			yaml_data = yaml.safe_load(yaml_file)

			camera_name = yaml_data['camera_name']
			distortion_model = yaml_data['distortion_model']

			width = yaml_data['image_width']
			height = yaml_data['image_height']
			K = np.array(yaml_data['camera_matrix']['data']).reshape(3, 3)
			D = np.array(yaml_data['distortion_coefficients']['data']).reshape(1, 5)
			Rect = np.array(yaml_data['rectification_matrix']['data']).reshape(3, 3)
			P = np.array(yaml_data['projection_matrix']['data']).reshape(3, 4)
			
			translation = np.array(yaml_data['translation_stereo']['data'])
			quaternion = np.array(yaml_data['quaternion_stereo']['data'])
			T_stereo = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])

			if 'sensor_body_imu' in yaml_data:
				translation = np.array(yaml_data['translation_sensor_body_imu']['data'])
				quaternion = np.array(yaml_data['quaternion_sensor_body_imu']['data'])
				T_sensor_bodyimu = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])
				self.extrinsics_collection[frame_id]['body_imu'] = T_sensor_bodyimu
				self.extrinsics_collection['body_imu'][frame_id] = np.linalg.inv(T_sensor_bodyimu)

			camera = CameraPinhole(width, height, camera_name, distortion_model, K, D, Rect, P, T_stereo)	
			if self.is_print:
				print(camera)
			self.sensor_collection[sensor] = camera

	# NOTE(gogojjh): can only handle pinhole camera
	def load_event_camera(self, sensor, frame_id, yaml_path):
		with open(yaml_path, 'r') as yaml_file:
			yaml_data = yaml.safe_load(yaml_file)

			camera_name = yaml_data['camera_name']
			distortion_model = yaml_data['distortion_model']

			width = yaml_data['image_width']
			height = yaml_data['image_height']
			K = np.array(yaml_data['camera_matrix']['data']).reshape(3, 3)
			D = np.array(yaml_data['distortion_coefficients']['data']).reshape(1, 5)
			Rect = np.array(yaml_data['rectification_matrix']['data']).reshape(3, 3)
			P = np.array(yaml_data['projection_matrix']['data']).reshape(3, 4)
			
			translation = np.array(yaml_data['translation_stereo']['data'])
			quaternion = np.array(yaml_data['quaternion_stereo']['data'])
			print(quaternion)
			print(quaternion[[1, 2, 3, 0]])
			T_stereo = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])

			translation = np.array(yaml_data['translation_sensor_body_imu']['data'])
			quaternion = np.array(yaml_data['quaternion_sensor_body_imu']['data'])
			T_sensor_bodyimu = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])
			self.extrinsics_collection[frame_id]['body_imu'] = T_sensor_bodyimu			
			self.extrinsics_collection['body_imu'][frame_id] = np.linalg.inv(T_sensor_bodyimu)

			eventimu_frameid = '{}_imu'.format(frame_id)
			if eventimu_frameid in yaml_data:
				translation = np.array(yaml_data['translation_sensor_{}'.format(eventimu_frameid)]['data'])
				quaternion = np.array(yaml_data['quaternion_sensor_{}'.format(eventimu_frameid)]['data'])
				T_sensor_eventimu = eigen_conversion.convert_vec_to_matrix(translation, quaternion[[1, 2, 3, 0]])
				self.extrinsics_collection[frame_id][eventimu_frameid] = T_sensor_eventimu			
				self.extrinsics_collection[eventimu_frameid][frame_id] = np.linalg.inv(T_sensor_eventimu)

			camera = CameraPinhole(width, height, camera_name, distortion_model, K, D, Rect, P, T_stereo)	
			if self.is_print:
				print(camera)
			self.sensor_collection[sensor] = camera

if __name__ == "__main__":
	sys.path.append('cfg')
	from dataset.cfg_vehicle import dataset_sensor_frameid_dict
	int_ext_loader = IntrinsicExtrinsicLoader(is_print=True)
																						
	int_ext_loader.load_calibration(calib_path='/Titan/dataset/FusionPortable_dataset_develop/calibration_files/20230618_calib/calib', \
																	sensor_frameid_dict=dataset_sensor_frameid_dict)