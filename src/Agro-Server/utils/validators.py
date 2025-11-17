"""
Validadores para dados de entrada das APIs de Units e Occurrences
"""

def validar_unit(data: dict) -> tuple[bool, str]:
    """
    Valida dados de Unit.
    Retorna (é_valido, mensagem_erro)
    """
    if not data:
        return False, "Dados não fornecidos"
    
    # name é obrigatório
    if "name" not in data or not data.get("name"):
        return False, "Campo 'name' é obrigatório"
    
    # name deve ser string
    if not isinstance(data.get("name"), str):
        return False, "Campo 'name' deve ser uma string"
    
    # description é opcional, mas se presente deve ser string
    if "description" in data and data["description"] is not None:
        if not isinstance(data["description"], str):
            return False, "Campo 'description' deve ser uma string"
    
    return True, ""

def validar_occurrence(data: dict) -> tuple[bool, str]:
    """
    Valida dados de Occurrence.
    Retorna (é_valido, mensagem_erro)
    """
    if not data:
        return False, "Dados não fornecidos"
    
    # Campos obrigatórios
    campos_obrigatorios = ["travel_id", "unit_id", "category_id", "datetime"]
    for campo in campos_obrigatorios:
        if campo not in data or data.get(campo) is None:
            return False, f"Campo '{campo}' é obrigatório"
    
    # Validações de tipo
    if not isinstance(data.get("travel_id"), (int, str)):
        return False, "Campo 'travel_id' deve ser um número"
    
    if not isinstance(data.get("unit_id"), (int, str)):
        return False, "Campo 'unit_id' deve ser um número"
    
    if not isinstance(data.get("category_id"), (int, str)):
        return False, "Campo 'category_id' deve ser um número"
    
    # carrier_name, root_cause, description são opcionais
    # mas se presentes devem ser strings
    campos_opcionais = ["carrier_name", "root_cause", "description"]
    for campo in campos_opcionais:
        if campo in data and data[campo] is not None:
            if not isinstance(data[campo], str):
                return False, f"Campo '{campo}' deve ser uma string"
    
    return True, ""

def validar_id(id_value) -> tuple[bool, str]:
    """
    Valida se um ID é válido (não None e não vazio)
    """
    if id_value is None:
        return False, "ID não fornecido"
    
    if isinstance(id_value, str) and not id_value.strip():
        return False, "ID não pode ser vazio"
    
    return True, ""

