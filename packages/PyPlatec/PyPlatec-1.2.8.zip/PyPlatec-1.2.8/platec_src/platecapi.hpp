/******************************************************************************
 *  PlaTec, a 2D terrain generator based on plate tectonics
 *  Copyright (C) 2012- Lauri Viitanen
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, see http://www.gnu.org/licenses/
 *****************************************************************************/

#ifndef PLATECAPI_H
#define PLATECAPI_H

#include <string.h> // For size_t.

void *  platec_api_create(
	    long seed,
        size_t width,
        size_t height,
        float sea_level,
        size_t erosion_period, float folding_ratio,
        size_t aggr_overlap_abs, float aggr_overlap_rel,
        size_t cycle_count, size_t num_plates);

void    platec_api_destroy(void*);
const size_t* platec_api_get_agemap(size_t);
float* platec_api_get_heightmap(void*);
size_t* platec_api_get_platesmap(void*);
size_t  platec_api_is_finished(void*);
void    platec_api_step(void*);

size_t lithosphere_getMapWidth ( void* object);
size_t lithosphere_getMapHeight ( void* object);

#endif
