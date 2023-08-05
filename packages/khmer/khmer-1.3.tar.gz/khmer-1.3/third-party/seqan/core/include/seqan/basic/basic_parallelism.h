// ==========================================================================
//                 SeqAn - The Library for Sequence Analysis
// ==========================================================================
// Copyright (c) 2006-2013, Knut Reinert, FU Berlin
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//     * Neither the name of Knut Reinert or the FU Berlin nor the names of
//       its contributors may be used to endorse or promote products derived
//       from this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL KNUT REINERT OR THE FU BERLIN BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
// DAMAGE.
//
// ==========================================================================
// Author: Manuel Holtgrewe <manuel.holtgrewe@fu-berlin.de>
// ==========================================================================
// This sub module contains simple, generic support code for parallelism in
// SeqAn.
//
// It mainly defines the macro SEQAN_ENABLE_PARALLELISM.
// ==========================================================================

#ifndef SEQAN_CORE_INCLUDE_SEQAN_BASIC_BASIC_PARALLELISM_H_
#define SEQAN_CORE_INCLUDE_SEQAN_BASIC_BASIC_PARALLELISM_H_

/**
.Macro.SEQAN_ENABLE_PARALLELISM
..summary:Indicates whether parallelism is enabled with value 0/1.
..cat:Parallelism
..signature:SEQAN_ENABLE_PARALLELISM
..remarks:By default, set to 1 if $_OPENMP$ is defined and set to 0 otherwise.
..example:If you want to change this value, you have to define this value before including any SeqAn header.
...code:#define SEQAN_ENABLE_PARALLELISM 0  // ALWAYS switch off parallelism!

#include <seqan/basic.h>

int main(int argc, char ** argv)
{
  return 0;
}
..include:seqan/basic.h
 */

#if !defined(SEQAN_ENABLE_PARALLELISM)
#if defined(_OPENMP)
#define SEQAN_ENABLE_PARALLELISM 1
#else  // defined(_OPENMP)
#define SEQAN_ENABLE_PARALLELISM 0
#endif  // defined(_OPENMP)
#endif  // !defined(SEQAN_ENABLE_PARALLELISM)

#endif  // SEQAN_CORE_INCLUDE_SEQAN_BASIC_BASIC_PARALLELISM_H_
