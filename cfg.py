"""Générateur de Graphe de Flux de Contrôle (CFG) à partir de l'AST"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from ast_nodes import *

@dataclass
class NoeudCFG:
    """Nœud dans le CFG"""
    id: int
    etiquette: str  # Description du nœud
    type_noeud: str  # "entree", "sortie", "instruction", "condition", "appel"
    noeud_ast: Optional[Union[Instruction, Expression]] = None
    
    def __str__(self):
        return f"Noeud{self.id}({self.type_noeud}): {self.etiquette}"

@dataclass 
class AreteCFG:
    """Arête dans le CFG"""
    noeud_source: int
    noeud_cible: int
    etiquette: str = ""  # "vrai", "faux", "" pour normal
    
    def __str__(self):
        return f"{self.noeud_source} -> {self.noeud_cible}" + (f" [{self.etiquette}]" if self.etiquette else "")

@dataclass
class GrapheFluxControle:
    """Graphe de flux de contrôle"""
    nom_fonction: str
    noeuds: Dict[int, NoeudCFG] = field(default_factory=dict)
    aretes: List[AreteCFG] = field(default_factory=list)
    noeud_entree: Optional[int] = None
    noeud_sortie: Optional[int] = None
    
    def ajouter_noeud(self, noeud: NoeudCFG) -> int:
        """Ajouter un nœud au CFG"""
        self.noeuds[noeud.id] = noeud
        return noeud.id
    
    def ajouter_arete(self, id_source: int, id_cible: int, etiquette: str = "") -> None:
        """Ajouter une arête au CFG"""
        self.aretes.append(AreteCFG(id_source, id_cible, etiquette))
    
    def obtenir_successeurs(self, id_noeud: int) -> List[int]:
        """Obtenir les successeurs d'un nœud"""
        return [arete.noeud_cible for arete in self.aretes if arete.noeud_source == id_noeud]
    
    def obtenir_predecesseurs(self, id_noeud: int) -> List[int]:
        """Obtenir les prédécesseurs d'un nœud"""
        return [arete.noeud_source for arete in self.aretes if arete.noeud_cible == id_noeud]
    
    def afficher_graphe(self) -> None:
        """Afficher le CFG en mode texte"""
        print(f"\nCFG pour la fonction '{self.nom_fonction}':")
        print("=" * 50)
        
        print(f"Entrée: Noeud{self.noeud_entree}")
        print(f"Sortie: Noeud{self.noeud_sortie}")
        print()
        
        print("Nœuds:")
        for id_noeud in sorted(self.noeuds.keys()):
            noeud = self.noeuds[id_noeud]
            print(f"  {noeud}")
        
        print("\nArêtes:")
        for arete in self.aretes:
            print(f"  {arete}")
        print()

class ConstructeurCFG:
    """Constructeur de CFG"""
    
    def __init__(self):
        self.prochain_id = 0
        self.cfg = None
        self.cibles_arret: List[int] = []    # Pile des cibles de break
        self.cibles_continuer: List[int] = []  # Pile des cibles de continue
    
    def nouveau_noeud(self, etiquette: str, type_noeud: str, noeud_ast: Optional[Union[Instruction, Expression]] = None) -> NoeudCFG:
        """Créer un nouveau nœud avec ID unique"""
        noeud = NoeudCFG(self.prochain_id, etiquette, type_noeud, noeud_ast)
        self.prochain_id += 1
        return noeud
    
    def construire_cfg_fonction(self, fonction: DefinitionFonction) -> GrapheFluxControle:
        """Construire le CFG pour une fonction"""
        self.cfg = GrapheFluxControle(fonction.nom)
        self.prochain_id = 0
        self.cibles_arret = []
        self.cibles_continuer = []
        
        # Nœud d'entrée
        entree = self.nouveau_noeud(f"Entry: {fonction.nom}", "entree")
        self.cfg.ajouter_noeud(entree)
        self.cfg.noeud_entree = entree.id
        
        # Nœud de sortie
        noeud_sortie = self.nouveau_noeud(f"Exit: {fonction.nom}", "sortie")
        self.cfg.ajouter_noeud(noeud_sortie)
        self.cfg.noeud_sortie = noeud_sortie.id
        
        # Construire le CFG du corps de la fonction
        entree_corps, sorties_corps = self.construire_cfg_instruction(fonction.corps)
        
        # Connecter l'entrée au corps
        if entree_corps is not None:
            self.cfg.ajouter_arete(entree.id, entree_corps)
        else:
            # Corps vide, connecter directement à la sortie
            self.cfg.ajouter_arete(entree.id, noeud_sortie.id)
        
        # Connecter les sorties du corps à la sortie
        for id_sortie in sorties_corps:
            self.cfg.ajouter_arete(id_sortie, noeud_sortie.id)
        
        return self.cfg
    
    def construire_cfg_instruction(self, instruction: Instruction) -> Tuple[Optional[int], List[int]]:
        """
        Construire le CFG pour une instruction
        Retourne: (nœud d'entrée, liste des nœuds de sortie)
        """
        if isinstance(instruction, Bloc):
            return self.construire_cfg_bloc(instruction)
        elif isinstance(instruction, InstructionSi):
            return self.construire_cfg_si(instruction)
        elif isinstance(instruction, BoucleTantQue):
            return self.construire_cfg_tant_que(instruction)
        elif isinstance(instruction, BouclePour):
            return self.construire_cfg_pour(instruction)
        elif isinstance(instruction, InstructionRetour):
            return self.construire_cfg_retour(instruction)
        elif isinstance(instruction, InstructionArret):
            return self.construire_cfg_arret(instruction)
        elif isinstance(instruction, InstructionContinuer):
            return self.construire_cfg_continuer(instruction)
        elif isinstance(instruction, Declaration):
            return self.construire_cfg_declaration(instruction)
        elif isinstance(instruction, Assignation):
            return self.construire_cfg_assignation(instruction)
        elif isinstance(instruction, InstructionExpression):
            return self.construire_cfg_instruction_expression(instruction)
        else:
            # Instruction inconnue, traiter comme instruction simple
            noeud = self.nouveau_noeud("Instruction inconnue", "instruction", instruction)
            self.cfg.ajouter_noeud(noeud)
            return noeud.id, [noeud.id]
    
    def construire_cfg_bloc(self, bloc: Bloc) -> Tuple[Optional[int], List[int]]:
        """CFG pour un bloc d'instructions"""
        if not bloc.instructions:
            return None, []
        
        entree = None
        sorties_actuelles = []
        
        for instruction in bloc.instructions:
            entree_instruction, sorties_instruction = self.construire_cfg_instruction(instruction)
            
            if entree is None:
                # Première instruction du bloc
                entree = entree_instruction
            else:
                # Connecter les sorties précédentes à l'entrée actuelle
                if entree_instruction is not None:
                    for id_sortie in sorties_actuelles:
                        self.cfg.ajouter_arete(id_sortie, entree_instruction)
            
            sorties_actuelles = sorties_instruction
        
        return entree, sorties_actuelles
    
    def construire_cfg_si(self, instruction_si: InstructionSi) -> Tuple[Optional[int], List[int]]:
        """CFG pour if/else"""
        # Nœud de condition
        noeud_condition = self.nouveau_noeud(f"if ({self.expression_vers_chaine(instruction_si.condition)})", "condition", instruction_si.condition)
        self.cfg.ajouter_noeud(noeud_condition)
        
        # Branche vraie (alors)
        entree_alors, sorties_alors = self.construire_cfg_instruction(instruction_si.instruction_alors)
        if entree_alors is not None:
            self.cfg.ajouter_arete(noeud_condition.id, entree_alors, "vrai")
        
        # Branche fausse (sinon)
        toutes_sorties = []
        
        if instruction_si.instruction_sinon:
            entree_sinon, sorties_sinon = self.construire_cfg_instruction(instruction_si.instruction_sinon)
            if entree_sinon is not None:
                self.cfg.ajouter_arete(noeud_condition.id, entree_sinon, "faux")
            toutes_sorties.extend(sorties_sinon)
        else:
            # Pas de sinon, la condition peut directement sortir
            toutes_sorties.append(noeud_condition.id)
        
        # Ajouter les sorties du alors
        toutes_sorties.extend(sorties_alors)
        
        return noeud_condition.id, toutes_sorties
    
    def construire_cfg_tant_que(self, boucle_tant_que: BoucleTantQue) -> Tuple[Optional[int], List[int]]:
        """CFG pour while"""
        # Nœud de condition
        noeud_condition = self.nouveau_noeud(f"while ({self.expression_vers_chaine(boucle_tant_que.condition)})", "condition", boucle_tant_que.condition)
        self.cfg.ajouter_noeud(noeud_condition)
        
        # Nœud de sortie de boucle (pour break et condition fausse)
        sortie_boucle = self.nouveau_noeud("sortie_while", "instruction")
        self.cfg.ajouter_noeud(sortie_boucle)
        
        # Ajouter les cibles break/continue
        self.cibles_arret.append(sortie_boucle.id)
        self.cibles_continuer.append(noeud_condition.id)
        
        # Corps de la boucle
        entree_corps, sorties_corps = self.construire_cfg_instruction(boucle_tant_que.corps)
        
        # Retirer les cibles break/continue
        self.cibles_arret.pop()
        self.cibles_continuer.pop()
        
        # Connecter condition -> corps (vrai)
        if entree_corps is not None:
            self.cfg.ajouter_arete(noeud_condition.id, entree_corps, "vrai")
        
        # Connecter condition -> sortie (faux)
        self.cfg.ajouter_arete(noeud_condition.id, sortie_boucle.id, "faux")
        
        # Connecter sorties du corps -> condition (boucle)
        for id_sortie in sorties_corps:
            self.cfg.ajouter_arete(id_sortie, noeud_condition.id)
        
        return noeud_condition.id, [sortie_boucle.id]
    
    def construire_cfg_pour(self, boucle_pour: BouclePour) -> Tuple[Optional[int], List[int]]:
        """CFG pour for"""
        entree_actuelle = None
        sorties_actuelles = []
        
        # Initialisation
        if boucle_pour.initialisation:
            entree_init, sorties_init = self.construire_cfg_instruction(boucle_pour.initialisation)
            entree_actuelle = entree_init
            sorties_actuelles = sorties_init
        
        # Condition
        if boucle_pour.condition:
            noeud_condition = self.nouveau_noeud(f"for_cond ({self.expression_vers_chaine(boucle_pour.condition)})", "condition", boucle_pour.condition)
            self.cfg.ajouter_noeud(noeud_condition)
            
            # Connecter init -> condition
            for id_sortie in sorties_actuelles:
                self.cfg.ajouter_arete(id_sortie, noeud_condition.id)
            
            if entree_actuelle is None:
                entree_actuelle = noeud_condition.id
                
            id_condition = noeud_condition.id
        else:
            # Pas de condition, créer un nœud fictif
            noeud_condition = self.nouveau_noeud("for_cond (vrai)", "instruction")
            self.cfg.ajouter_noeud(noeud_condition)
            
            for id_sortie in sorties_actuelles:
                self.cfg.ajouter_arete(id_sortie, noeud_condition.id)
                
            if entree_actuelle is None:
                entree_actuelle = noeud_condition.id
                
            id_condition = noeud_condition.id
        
        # Nœud de sortie
        sortie_boucle = self.nouveau_noeud("sortie_for", "instruction")
        self.cfg.ajouter_noeud(sortie_boucle)
        
        # Mise à jour
        id_mise_a_jour = id_condition  # Par défaut, continue va vers la condition
        if boucle_pour.mise_a_jour:
            entree_maj, sorties_maj = self.construire_cfg_instruction(boucle_pour.mise_a_jour)
            if entree_maj is not None:
                id_mise_a_jour = entree_maj
                # Connecter mise à jour -> condition
                for id_sortie in sorties_maj:
                    self.cfg.ajouter_arete(id_sortie, id_condition)
        
        # Ajouter cibles break/continue
        self.cibles_arret.append(sortie_boucle.id)
        self.cibles_continuer.append(id_mise_a_jour)
        
        # Corps
        entree_corps, sorties_corps = self.construire_cfg_instruction(boucle_pour.corps)
        
        # Retirer cibles
        self.cibles_arret.pop()
        self.cibles_continuer.pop()
        
        # Connecter condition -> corps (vrai)
        if entree_corps is not None:
            self.cfg.ajouter_arete(id_condition, entree_corps, "vrai")
        
        # Connecter condition -> sortie (faux)
        self.cfg.ajouter_arete(id_condition, sortie_boucle.id, "faux")
        
        # Connecter corps -> mise à jour
        for id_sortie in sorties_corps:
            self.cfg.ajouter_arete(id_sortie, id_mise_a_jour)
        
        return entree_actuelle, [sortie_boucle.id]
    
    def construire_cfg_retour(self, instruction_retour: InstructionRetour) -> Tuple[Optional[int], List[int]]:
        """CFG pour return"""
        if instruction_retour.valeur:
            etiquette = f"return {self.expression_vers_chaine(instruction_retour.valeur)}"
        else:
            etiquette = "return"
        
        noeud = self.nouveau_noeud(etiquette, "retour", instruction_retour)
        self.cfg.ajouter_noeud(noeud)
        
        # Return va toujours vers la sortie de fonction
        if self.cfg.noeud_sortie is not None:
            self.cfg.ajouter_arete(noeud.id, self.cfg.noeud_sortie)
        
        return noeud.id, []  # Pas de sortie normale (va vers exit)
    
    def construire_cfg_arret(self, instruction_arret: InstructionArret) -> Tuple[Optional[int], List[int]]:
        """CFG pour break"""
        noeud = self.nouveau_noeud("break", "arret", instruction_arret)
        self.cfg.ajouter_noeud(noeud)
        
        # Break va vers la cible de break la plus récente
        if self.cibles_arret:
            self.cfg.ajouter_arete(noeud.id, self.cibles_arret[-1])
        
        return noeud.id, []  # Pas de sortie normale
    
    def construire_cfg_continuer(self, instruction_continuer: InstructionContinuer) -> Tuple[Optional[int], List[int]]:
        """CFG pour continue"""
        noeud = self.nouveau_noeud("continue", "continuer", instruction_continuer)  
        self.cfg.ajouter_noeud(noeud)
        
        # Continue va vers la cible de continue la plus récente
        if self.cibles_continuer:
            self.cfg.ajouter_arete(noeud.id, self.cibles_continuer[-1])
        
        return noeud.id, []  # Pas de sortie normale
    
    def construire_cfg_declaration(self, declaration: Declaration) -> Tuple[Optional[int], List[int]]:
        """CFG pour déclaration"""
        if declaration.initialisateur:
            etiquette = f"{declaration.type_variable.value} {declaration.nom_variable} = {self.expression_vers_chaine(declaration.initialisateur)}"
        else:
            etiquette = f"{declaration.type_variable.value} {declaration.nom_variable}"
        
        noeud = self.nouveau_noeud(etiquette, "instruction", declaration)
        self.cfg.ajouter_noeud(noeud)
        return noeud.id, [noeud.id]
    
    def construire_cfg_assignation(self, assignation: Assignation) -> Tuple[Optional[int], List[int]]:
        """CFG pour assignation"""
        chaine_cible = self.expression_vers_chaine(assignation.cible)
        chaine_valeur = self.expression_vers_chaine(assignation.valeur)
        etiquette = f"{chaine_cible} = {chaine_valeur}"
        
        noeud = self.nouveau_noeud(etiquette, "instruction", assignation)
        self.cfg.ajouter_noeud(noeud)
        return noeud.id, [noeud.id]
    
    def construire_cfg_instruction_expression(self, instruction_expression: InstructionExpression) -> Tuple[Optional[int], List[int]]:
        """CFG pour instruction expression"""
        etiquette = self.expression_vers_chaine(instruction_expression.expression)
        
        # Détecter les appels de fonction
        if isinstance(instruction_expression.expression, AppelFonction):
            type_noeud = "appel"
        else:
            type_noeud = "instruction"
        
        noeud = self.nouveau_noeud(etiquette, type_noeud, instruction_expression)
        self.cfg.ajouter_noeud(noeud)
        return noeud.id, [noeud.id]
    
    def expression_vers_chaine(self, expr: Expression) -> str:
        """Convertir une expression en string lisible"""
        if isinstance(expr, LitteralEntier):
            return str(expr.valeur)
        elif isinstance(expr, LitteralFlottant):
            return str(expr.valeur)
        elif isinstance(expr, LitteralChaine):
            return f'"{expr.valeur}"'
        elif isinstance(expr, LitteralCaractere):
            return f"'{expr.valeur}'"
        elif isinstance(expr, LitteralBooleen):
            return "vrai" if expr.valeur else "faux"
        elif isinstance(expr, Identifiant):
            return expr.nom
        elif isinstance(expr, ExpressionBinaire):
            gauche = self.expression_vers_chaine(expr.gauche)
            droite = self.expression_vers_chaine(expr.droite)
            return f"({gauche} {expr.operateur.value} {droite})"
        elif isinstance(expr, ExpressionUnaire):
            operande = self.expression_vers_chaine(expr.operande)
            if expr.operateur in [OperateurUnaire.PRE_INCREMENTATION, OperateurUnaire.PRE_DECREMENTATION]:
                return f"{expr.operateur.value}{operande}"
            elif expr.operateur in [OperateurUnaire.POST_INCREMENTATION, OperateurUnaire.POST_DECREMENTATION]:
                return f"{operande}{expr.operateur.value}"
            else:
                return f"{expr.operateur.value}{operande}"
        elif isinstance(expr, AppelFonction):
            arguments = ", ".join(self.expression_vers_chaine(arg) for arg in expr.arguments)
            return f"{expr.nom_fonction}({arguments})"
        elif isinstance(expr, AccesTableau):
            tableau = self.expression_vers_chaine(expr.tableau)
            indice = self.expression_vers_chaine(expr.indice)
            return f"{tableau}[{indice}]"
        else:
            return "???"

def construire_cfg(programme: Programme) -> List[GrapheFluxControle]:
    """Construire les CFG pour toutes les fonctions du programme"""
    cfgs = []
    constructeur = ConstructeurCFG()
    
    for fonction in programme.fonctions:
        cfg = constructeur.construire_cfg_fonction(fonction)
        cfgs.append(cfg)
    
    return cfgs

# Test simple
if __name__ == "__main__":
    from parser import analyser_chaine
    
    code_test = '''
    int factorielle(int n) {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorielle(n - 1);
        }
    }
    '''
    
    try:
        ast = analyser_chaine(code_test)
        cfgs = construire_cfg(ast)
        
        for cfg in cfgs:
            cfg.afficher_graphe()
            
    except Exception as e:
        print(f"Erreur: {e}")