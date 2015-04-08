
open Nethtml

module Mint = Map.Make(struct type t = int let compare = Pervasives.compare end)

let get_page url = Http_client.Convenience.http_get url

let parse_base page = parse_document (Lexing.from_string page)

let aux = function
    | Element(s, _, _) -> Format.printf "%s@." s
    | Data s -> Format.printf "?%s@." s

let test doc = List.iter aux doc

let is_elt = function
    | Element(_,_, _) -> true
    | _ -> false

let is_dat x = not (is_elt x)

let is_table = function
    | Element("table",_, _) -> true
    | _ -> false

let to_int l = match (List.filter is_dat l) with
    | Data s :: _ -> int_of_string s
    | _ -> Format.printf "6@."; raise Exit

let to_string l = match (List.filter is_dat l) with
    | Data s :: _ -> s
    | [] -> ""
    | _ -> raise Exit

let parse_row m = function
    | Element("tr", _, l) -> begin match (List.filter is_elt l) with
        | Element("td", _, x) :: Element("td", _, y) :: Element("td", _, z) :: _ ->
                Mint.add (to_int x) (to_string y, to_string z) m
        | _ -> m
        end
    | _ -> m

let parse_table t =
    List.fold_left parse_row Mint.empty t

let to_arr m =
    let n, _ = Mint.max_binding m in
    Array.init n (fun i -> try Mint.find i m with Not_found -> "", "")

let parse page = match (List.filter is_elt (parse_base page)) with
    | [Element ("html", _, [_;_;_;b])] -> begin match b with
        | Element ("body", _, l) -> begin match (List.filter is_elt l) with
            | Element ("div", _, l) :: _ -> begin match (List.filter is_elt l) with
                | Element("div", _, l) :: _ -> begin match (List.filter is_table l) with
                    | Element("table", _, t) :: _ ->
                        to_arr (parse_table (List.filter is_elt t))
                    | _ -> Format.printf "1@.";raise Exit
                    end
                | _ ->  Format.printf "2@.";raise Exit
                end
            | _ ->  Format.printf "3@.";raise Exit
            end
        | _ ->  Format.printf "4@.";raise Exit
        end
    | _ ->  Format.printf "5@.";raise Exit

module M = Map.Make(struct type t = string let compare = compare end)

let st = ref M.empty

let get thurne =
    try
        M.find thurne !st
    with Not_found -> [], 0

let sincr thurne i =
    let score, n = get thurne in
    st := M.add thurne (i :: score, n + 1) !st

let add t = Array.iteri (fun i (_, thurne) -> sincr thurne i) t

let bindings () =
    List.filter (fun (_, (i,j)) -> List.fold_left (+) 0 i <> 0 && j <> 0) (M.bindings !st)

let url = [
    "http://www.dg.ens.fr/thurnage/2007/resultats-classement.html";
    "http://www.dg.ens.fr/thurnage/2008/resultats-classement.html";
    "http://www.dg.ens.fr/thurnage/2009/resultats-classement.html";
    "http://www.dg.ens.fr/thurnage/2010/resultats-classement.html";
    "http://www.dg.ens.fr/thurnage/2011/resultats-classement.html";
    "http://www.dg.ens.fr/thurnage/2012/resultats-classement.html";
    "http://www.dg.ens.fr/thurnage/2013/resultats-classement.html";
]

let lprinter fmt l =
  let rec inner fmt = function
    | [] -> ()
    | x :: xs -> Format.fprintf fmt "%d; %a" x inner xs
  in
  Format.fprintf fmt "[ %a ]" inner l

let main () =
    let pages = List.map get_page url in
    let rankings = List.map parse pages in
    List.iter add rankings;
    let order = bindings () in
    let order = List.map (fun (thurne, (i, j)) -> (thurne, ((List.fold_right (+.) (List.rev_map float i) 0.0)) /. (float j))) order in
    let order = List.sort (fun (_, i) (_, j) -> compare i j) order in
    List.iter (fun (thurne, score) -> Format.printf "%s : %a@." thurne lprinter (fst @@ get thurne)) (order)

;;
main ()
