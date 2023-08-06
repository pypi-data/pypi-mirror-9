
def check_dict_struct(value, required):

	if type(value) is not dict or type(required) is not dict:
		return False

	def check_node(val_node, req_node):
		for key in req_node:
			if key not in val_node:
				return False

			if type(val_node[key]) is dict:
				if type(req_node[key]) is not dict:
					return False

				if not check_node(val_node[key], req_node[key]):
					return False

			elif type(val_node[key]) is not req_node[key]:
				return False

		return True

	return check_node(value, required)