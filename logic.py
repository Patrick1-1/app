from libs import matplotlib, plt, gpd, io, base64, random, index, math, zipfile, os

def MakeLayerFromShape(path_to_geodata):
    # Open the shapefile
    layer = gpd.read_file(path_to_geodata)
    return(layer)

# Function for find line direction. If direction degree more 210 or less 110? we will think, taht this elements differend
def calculate_degree(layer, start_first_point, end_first_point, start_other_point, end_other_point, index_first, index_second):
    # Use vector math to find cosinus between two vector
    vec1 = (end_first_point[0] - start_first_point[0], end_first_point[1] - start_first_point[1])
    vec2 = (end_other_point[0] - start_other_point[0], end_other_point[1] - start_other_point[1])
    dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    magnitude1 = layer.loc[index_first, 'length']
    magnitude2 = layer.loc[index_second, 'length']
    cos_theta = dot_product / (magnitude1 * magnitude2)
    angle_radians = math.acos(cos_theta)
    angle_degrees = math.degrees(angle_radians)
    if 150 < angle_degrees or angle_degrees > 210:
        return(True)
    return(False)

def AnalyzeShape(layer):
    # Project geometry to Mercator and add technical field
    projected_layer = layer.to_crs(3857)
    projected_layer['new_id'] = projected_layer.index
    projected_layer['length'] = projected_layer['geometry'].length
    # Create and add geometry to spatial index
    spatial_index = index.Index()
    for idx, geometry in enumerate(projected_layer['geometry']):
        spatial_index.insert(idx, geometry.bounds)
    # Create lis with all identificator objects
    all_indexes = list(projected_layer['new_id'])
    # End list lines
    groups = []
    # List for index enumerate
    index_list = [0]
    # List for one road elements
    one_roads = []
    for idx, geometry in enumerate(projected_layer['geometry'], start=index_list[-1]):
        # Start point line
        start_point = geometry.coords[0]
        # End point line
        end_point = geometry.coords[-1]
        # Find indexes for intersect line with actual line for by using spatial intersect
        touching_indices = list(spatial_index.intersection(geometry.bounds))
        for elem in touching_indices:
            for obj in groups:
                if elem in obj:
                    touching_indices.remove(elem)
                    break
        # Delete index for line now
        try:
            touching_indices.remove(idx)  
        except Exception:
            continue
        # Is geometry touches
        for touching_idx in touching_indices:
            other_geometry = projected_layer['geometry'].iloc[touching_idx]
            other_start_point = other_geometry.coords[0]
            other_end_point = other_geometry.coords[-1]
            # If end point == start point next line and degree is normal (normal parameters describe in calculate_degree function),
            # we think that this elements is part of one road
            if end_point == other_start_point and calculate_degree(projected_layer, start_point,end_point, other_start_point, other_end_point, idx, touching_idx) == True:
                one_roads.append(projected_layer['new_id'][touching_idx])
                index_list.append(projected_layer['new_id'][touching_idx])
                break
            else:
                # We think, that elements is'nt part of one road
                if len(one_roads)>0:
                    different = set(all_indexes)-set(index_list)
                    index_list.append(list(different)[0])
                    groups.append(tuple(one_roads))
                    one_roads.clear()
                    break
    # For objects in one groups, create a joint attribute value to symbolize data
    for group in groups:
        for elem in group:
            projected_layer.loc[elem, 'symbol'] = str(groups.index(group))
    condition = (projected_layer['symbol'].isna())
    projected_layer.loc[condition, 'symbol'] = '0'
    # Unite lines with joint attribute
    dissolved_gdf = projected_layer.dissolve(by='symbol', aggfunc='sum')
    return(dissolved_gdf)

# Function for render geodata
def RenderLayer(layer):
    matplotlib.use('agg')
    colors = [random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'orange']) for _ in layer['new_id']]
    layer.plot(figsize=(10,10), color=colors)
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_new = base64.b64encode(buffer.read()).decode('utf-8')
    return(image_new)

# Function for load script
def MakeMapImage():
    # This function return graphic with symboliza dataset.
    return(RenderLayer(layer=AnalyzeShape(MakeLayerFromShape(path_to_geodata=(os.path.join(os.getcwd(), 'sample/roads.shp'))))))