-- Keep exact identifiers and hashes readable without changing class typography.
function Code(element)
  if not FORMAT:match('latex') or #element.text < 18 then
    return nil
  end
  local result = pandoc.List()
  for word in element.text:gmatch('%S+') do
    if #result > 0 then result:insert(pandoc.Space()) end
    if #word >= 18 and not word:find('[{}\\]') then
      result:insert(pandoc.RawInline('latex', '\\nolinkurl{' .. word .. '}'))
    else
      result:insert(pandoc.Code(word))
    end
  end
  return result
end
