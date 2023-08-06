// Attempt for a bitonic sort inspired from "OpenCL in Action"
// Each work-item treats 2*4 elements so if max_workgroup_size = 512 up to 4096 items can be sorted (nvidia GPU)
// Uses local memory:
//     each work-item stores a 2*sizeof(float4), so the memory used for 512 working-elements is 16k (may not fit into pre-fermi GPUs)

#define VECTOR_SORT(input, dir) \
        comp = abs(input > shuffle(input, mask2)) ^ dir; \
        input = shuffle(input, comp * 2 + add2); \
        comp = abs(input > shuffle(input, mask1)) ^ dir; \
        input = shuffle(input, comp + add1); \

#define VECTOR_SWAP(in1, in2, dir) \
        input1 = in1; input2 = in2; \
        comp = (abs(input1 > input2) ^ dir) * 4 + add3; \
        in1 = shuffle2(input1, input2, comp); \
        in2 = shuffle2(input2, input1, comp); \

// Function to be called from an actual kernel.

float8 my_sort(uint local_id, uint group_id, uint local_size,
                float8 input, __local float4 *l_data){
    float4 input1, input2, temp;
    float8 output;
    uint4 comp, swap, mask1, mask2, add1, add2, add3;
    uint id, dir, size, stride;
    mask1 = (uint4)(1, 0, 3, 2);
    swap = (uint4)(0, 0, 1, 1);
    add1 = (uint4)(0, 0, 2, 2);
    mask2 = (uint4)(2, 3, 0, 1);
    add2 = (uint4)(0, 1, 0, 1);
    add3 = (uint4)(0, 1, 2, 3);

    // retrieve input data
    input1 = (float4)(input.s0, input.s1, input.s2, input.s3);
    input2 = (float4)(input.s4, input.s5, input.s6, input.s7);

    // Find global address
    id = local_id * 2;

    //Sort first vector

    comp = abs(input1 > shuffle(input1, mask1));
    input1 = shuffle(input1, comp ^ swap + add1);
    comp = abs(input1 > shuffle(input1, mask2));
    input1 = shuffle(input1, comp * 2 + add2);
    comp = abs(input1 > shuffle(input1, mask1));
    input1 = shuffle(input1, comp + add1);

    //Sort second vector
    comp = abs(input2 < shuffle(input2, mask1));
    input2 = shuffle(input2, comp ^ swap + add1);
    comp = abs(input2 < shuffle(input2, mask2));
    input2 = shuffle(input2, comp * 2 + add2);
    comp = abs(input2 < shuffle(input2, mask1));
    input2 = shuffle(input2, comp + add1);

    // Swap elements
    dir = local_id % 2;
    temp = input1;
    comp = (abs(input1 > input2) ^ dir) * 4 + add3;
    input1 = shuffle2(input1, input2, comp);
    input2 = shuffle2(input2, temp, comp);
    VECTOR_SORT(input1, dir);
    VECTOR_SORT(input2, dir);
    l_data[id] = input1;
    l_data[id+1] = input2;

    // Perform upper stages
    for(size = 2; size < local_size;    size <<= 1) {
        dir = local_id/size & 1;

        //Perform    lower stages
        for(stride = size; stride > 1; stride >>= 1) {
            barrier(CLK_LOCAL_MEM_FENCE);
            id = local_id +    (local_id/stride)*stride;
            VECTOR_SWAP(l_data[id],    l_data[id + stride], dir)
        }
        barrier(CLK_LOCAL_MEM_FENCE);

        id = local_id * 2;
        input1 = l_data[id];
        input2 = l_data[id+1];
        temp = input1;
        comp = (abs(input1 > input2) ^ dir) * 4 + add3;
        input1 = shuffle2(input1, input2, comp);
        input2 = shuffle2(input2, temp, comp);
        VECTOR_SORT(input1, dir);
        VECTOR_SORT(input2, dir);
        l_data[id] = input1;
        l_data[id+1] = input2;
    }
    dir = group_id % 2;

    // Perform bitonic merge
    for(stride = local_size; stride > 1; stride >>= 1) {
        barrier(CLK_LOCAL_MEM_FENCE);
        id = local_id +    (local_id/stride)*stride;
        VECTOR_SWAP(l_data[id], l_data[id + stride], dir)
    }
    barrier(CLK_LOCAL_MEM_FENCE);

    id = local_id * 2;
    input1 = l_data[id]; input2 = l_data[id+1];
    temp = input1;
    comp = (abs(input1 > input2) ^ dir) * 4 + add3;
    input1 = shuffle2(input1, input2, comp);
    input2 = shuffle2(input2, temp, comp);
    VECTOR_SORT(input1, dir);
    VECTOR_SORT(input2, dir);

    // setup output and return it
    output = (float8)(input1, input2);
    return  output;
}

__kernel void bsort_all(__global float4 *g_data,
                        __local float4 *l_data) {
    float4 input1, input2;
    float8 input, output;
    uint id, global_start;
    // Find global address
    id = get_local_id(0) * 2;
    global_start = get_group_id(0) * get_local_size(0) * 2 + id;

    input1 = g_data[global_start];
    input2 = g_data[global_start+1];
    input = (float8) (input1, input2);
    output = my_sort(get_local_id(0), get_group_id(0), get_local_size(0),
                    input, l_data);
    input1 = (float4) (output.s0, output.s1, output.s2, output.s3);
    input2 = (float4) (output.s4, output.s5, output.s6, output.s7);
    g_data[global_start] = input1;
    g_data[global_start+1] = input2;
}


// Perform the sort along the horizontal axis of a 2D image
// dim0 = y: wg=1
// dim1 = x: wg=number_of_element/8
//
__kernel void bsort_horizontal(__global float *g_data,
                                __local float4 *l_data) {
    float8 input, output;
    uint id, global_start, offset;

    // Find global address
    offset = get_global_size(1)*get_global_id(0)*8;
    id = get_local_id(1) * 8;
    global_start = offset + get_group_id(1) * get_local_size(1) * 8 + id;

    input = (float8)(g_data[global_start    ],
                     g_data[global_start + 1],
                     g_data[global_start + 2],
                     g_data[global_start + 3],
                     g_data[global_start + 4],
                     g_data[global_start + 5],
                     g_data[global_start + 6],
                     g_data[global_start + 7]);

    output = my_sort(get_local_id(1), get_group_id(1), get_local_size(1),
                   input, l_data);

    g_data[global_start    ] = output.s0;
    g_data[global_start + 1] = output.s1;
    g_data[global_start + 2] = output.s2;
    g_data[global_start + 3] = output.s3;
    g_data[global_start + 4] = output.s4;
    g_data[global_start + 5] = output.s5;
    g_data[global_start + 6] = output.s6;
    g_data[global_start + 7] = output.s7;
}


// Perform the sort along the vertical axis
// dim0 = y: wg=number_of_element/8
// dim1 = x: wg=1
// check if transposing +bsort_horizontal is not more efficient ?

__kernel void bsort_vertical(__global float *g_data,
                             __local float4 *l_data) {
    // we need to read 8 float position along the vertical axis
    float8 input, output;
    uint id, global_start, padding;

    // Find global address
    padding = get_global_size(1);
    id = get_local_id(0) * 8 * padding + get_global_id(1);
    global_start = get_group_id(0) * get_local_size(0) * 8 * padding + id;

	input = (float8)(g_data[global_start            ],
                     g_data[global_start + padding  ],
                     g_data[global_start + 2*padding],
                     g_data[global_start + 3*padding],
                     g_data[global_start + 4*padding],
                     g_data[global_start + 5*padding],
                     g_data[global_start + 6*padding],
                     g_data[global_start + 7*padding]);

      output = my_sort(get_local_id(0), get_group_id(0), get_local_size(0),
                       input, l_data);
      g_data[global_start             ] = output.s0;
      g_data[global_start + padding   ] = output.s1;
      g_data[global_start + 2*padding ] = output.s2;
      g_data[global_start + 3*padding ] = output.s3;
      g_data[global_start + 4*padding ] = output.s4;
      g_data[global_start + 5*padding ] = output.s5;
      g_data[global_start + 6*padding ] = output.s6;
      g_data[global_start + 7*padding ] = output.s7;
}


//Tested working reference kernel
__kernel void bsort(__global float4 *g_data,
                    __local float4 *l_data) {
    float4 input1, input2, temp;
    uint4 comp, swap, mask1, mask2, add1, add2, add3;
    uint id, dir, global_start, size, stride;
    mask1 = (uint4)(1, 0, 3, 2);
    swap = (uint4)(0, 0, 1, 1);
    add1 = (uint4)(0, 0, 2, 2);
    mask2 = (uint4)(2, 3, 0, 1);
    add2 = (uint4)(0, 1, 0, 1);
    add3 = (uint4)(0, 1, 2, 3);

    // Find global address
    id = get_local_id(0) * 2;
    global_start = get_group_id(0) * get_local_size(0) * 2 + id;

    //Sort first vector
    input1 = g_data[global_start];
    input2 = g_data[global_start+1];
    comp = abs(input1 > shuffle(input1, mask1));
    input1 = shuffle(input1, comp ^ swap + add1);
    comp = abs(input1 > shuffle(input1, mask2));
    input1 = shuffle(input1, comp * 2 + add2);
    comp = abs(input1 > shuffle(input1, mask1));
    input1 = shuffle(input1, comp + add1);

    //Sort second vector
    comp = abs(input2 < shuffle(input2, mask1));
    input2 = shuffle(input2, comp ^ swap + add1);
    comp = abs(input2 < shuffle(input2, mask2));
    input2 = shuffle(input2, comp * 2 + add2);
    comp = abs(input2 < shuffle(input2, mask1));
    input2 = shuffle(input2, comp + add1);

    // Swap elements
    dir = get_local_id(0) % 2;
    temp = input1;
    comp = (abs(input1 > input2) ^ dir) * 4 + add3;
    input1 = shuffle2(input1, input2, comp);
    input2 = shuffle2(input2, temp, comp);
    VECTOR_SORT(input1, dir);
    VECTOR_SORT(input2, dir);
    l_data[id] = input1;
    l_data[id+1] = input2;

    // Perform upper stages
    for(size = 2; size < get_local_size(0);    size <<= 1) {
        dir = get_local_id(0)/size & 1;

        //Perform    lower stages
        for(stride = size; stride > 1; stride >>= 1) {
            barrier(CLK_LOCAL_MEM_FENCE);
            id = get_local_id(0) +
            (get_local_id(0)/stride)*stride;
            VECTOR_SWAP(l_data[id],    l_data[id + stride], dir)
        }
        barrier(CLK_LOCAL_MEM_FENCE);

        id = get_local_id(0) * 2;
        input1 = l_data[id];
        input2 = l_data[id+1];
        temp = input1;
        comp = (abs(input1 > input2) ^ dir) * 4 + add3;
        input1 = shuffle2(input1, input2, comp);
        input2 = shuffle2(input2, temp, comp);
        VECTOR_SORT(input1, dir);
        VECTOR_SORT(input2, dir);
        l_data[id] = input1;
        l_data[id+1] = input2;
    }
    dir = get_group_id(0) % 2;
    // Perform bitonic merge
    for(stride = get_local_size(0); stride > 1;    stride >>= 1) {
        barrier(CLK_LOCAL_MEM_FENCE);
        id = get_local_id(0) +
        (get_local_id(0)/stride)*stride;
        VECTOR_SWAP(l_data[id], l_data[id + stride], dir)
    }
    barrier(CLK_LOCAL_MEM_FENCE);

    id = get_local_id(0) * 2;
    input1 = l_data[id]; input2 = l_data[id+1];
    temp = input1;
    comp = (abs(input1 > input2) ^ dir) * 4 + add3;
    input1 = shuffle2(input1, input2, comp);
    input2 = shuffle2(input2, temp, comp);
    VECTOR_SORT(input1, dir);
    VECTOR_SORT(input2, dir);
    g_data[global_start] = input1;
    g_data[global_start+1] = input2;
    }

