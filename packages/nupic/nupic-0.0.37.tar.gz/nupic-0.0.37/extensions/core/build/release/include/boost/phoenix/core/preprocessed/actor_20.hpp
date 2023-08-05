/*==============================================================================
    Copyright (c) 2005-2010 Joel de Guzman
    Copyright (c) 2010-2011 Thomas Heller

    Distributed under the Boost Software License, Version 1.0. (See accompanying
    file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
==============================================================================*/
        struct assign
            : proto::or_<
                proto::when< proto::nary_expr<proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) , assign( proto::_child_c< 13> , proto::call< proto::_child_c< 13>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) , assign( proto::_child_c< 13> , proto::call< proto::_child_c< 13>(proto::_state) > ) , assign( proto::_child_c< 14> , proto::call< proto::_child_c< 14>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) , assign( proto::_child_c< 13> , proto::call< proto::_child_c< 13>(proto::_state) > ) , assign( proto::_child_c< 14> , proto::call< proto::_child_c< 14>(proto::_state) > ) , assign( proto::_child_c< 15> , proto::call< proto::_child_c< 15>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) , assign( proto::_child_c< 13> , proto::call< proto::_child_c< 13>(proto::_state) > ) , assign( proto::_child_c< 14> , proto::call< proto::_child_c< 14>(proto::_state) > ) , assign( proto::_child_c< 15> , proto::call< proto::_child_c< 15>(proto::_state) > ) , assign( proto::_child_c< 16> , proto::call< proto::_child_c< 16>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) , assign( proto::_child_c< 13> , proto::call< proto::_child_c< 13>(proto::_state) > ) , assign( proto::_child_c< 14> , proto::call< proto::_child_c< 14>(proto::_state) > ) , assign( proto::_child_c< 15> , proto::call< proto::_child_c< 15>(proto::_state) > ) , assign( proto::_child_c< 16> , proto::call< proto::_child_c< 16>(proto::_state) > ) , assign( proto::_child_c< 17> , proto::call< proto::_child_c< 17>(proto::_state) > ) > > , proto::when< proto::nary_expr<proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ , proto::_ > , proto::and_< assign( proto::_child_c< 0> , proto::call< proto::_child_c< 0>(proto::_state) > ) , assign( proto::_child_c< 1> , proto::call< proto::_child_c< 1>(proto::_state) > ) , assign( proto::_child_c< 2> , proto::call< proto::_child_c< 2>(proto::_state) > ) , assign( proto::_child_c< 3> , proto::call< proto::_child_c< 3>(proto::_state) > ) , assign( proto::_child_c< 4> , proto::call< proto::_child_c< 4>(proto::_state) > ) , assign( proto::_child_c< 5> , proto::call< proto::_child_c< 5>(proto::_state) > ) , assign( proto::_child_c< 6> , proto::call< proto::_child_c< 6>(proto::_state) > ) , assign( proto::_child_c< 7> , proto::call< proto::_child_c< 7>(proto::_state) > ) , assign( proto::_child_c< 8> , proto::call< proto::_child_c< 8>(proto::_state) > ) , assign( proto::_child_c< 9> , proto::call< proto::_child_c< 9>(proto::_state) > ) , assign( proto::_child_c< 10> , proto::call< proto::_child_c< 10>(proto::_state) > ) , assign( proto::_child_c< 11> , proto::call< proto::_child_c< 11>(proto::_state) > ) , assign( proto::_child_c< 12> , proto::call< proto::_child_c< 12>(proto::_state) > ) , assign( proto::_child_c< 13> , proto::call< proto::_child_c< 13>(proto::_state) > ) , assign( proto::_child_c< 14> , proto::call< proto::_child_c< 14>(proto::_state) > ) , assign( proto::_child_c< 15> , proto::call< proto::_child_c< 15>(proto::_state) > ) , assign( proto::_child_c< 16> , proto::call< proto::_child_c< 16>(proto::_state) > ) , assign( proto::_child_c< 17> , proto::call< proto::_child_c< 17>(proto::_state) > ) , assign( proto::_child_c< 18> , proto::call< proto::_child_c< 18>(proto::_state) > ) > >
              , proto::when<
                    proto::terminal<proto::_>
                  , do_assign(proto::_, proto::_state)
                >
            >
        {};
