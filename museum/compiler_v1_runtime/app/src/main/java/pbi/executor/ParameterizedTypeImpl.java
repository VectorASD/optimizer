package pbi.executor;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.lang.reflect.TypeVariable;
import java.util.Arrays;
import java.util.Objects;
import pbi.executor.exceptions.ValueError;

public class ParameterizedTypeImpl implements ParameterizedType {
  private final Type[]   actualTypeArguments;
  private final Class<?> rawType;
  private final Type     ownerType;

  private ParameterizedTypeImpl(Class<?> rawType, Type[] actualTypeArguments, Type ownerType) throws ValueError {
    this.actualTypeArguments = actualTypeArguments;
    this.rawType             = rawType;
    this.ownerType           = (ownerType != null) ? ownerType : rawType.getDeclaringClass();
    validateConstructorArguments();
  }

  private void validateConstructorArguments() throws ValueError {
    TypeVariable<?>[] formals = rawType.getTypeParameters();
    if (formals.length != actualTypeArguments.length)
      throw new ValueError("Ожидалось " + formals.length + " параметров в параметизированном типе, а пришло " + actualTypeArguments.length);
    //for (int i = 0; i < actualTypeArguments.length; i++) {
      // check actuals against formals' bounds
    //}
  }

  public static ParameterizedTypeImpl make(Class<?> rawType, Type[] actualTypeArguments, Type ownerType) throws ValueError {
    return new ParameterizedTypeImpl(rawType, actualTypeArguments, ownerType);
  }
  public static ParameterizedTypeImpl make(Class<?> rawType, Type[] actualTypeArguments) throws ValueError {
    return new ParameterizedTypeImpl(rawType, actualTypeArguments, null);
  }

  public Type[] getActualTypeArguments() {
    return actualTypeArguments.clone();
  }

  public Class<?> getRawType() {
    return rawType;
  }

  public Type getOwnerType() {
    return ownerType;
  }

  @Override
  public boolean equals(Object o) {
    if (o instanceof ParameterizedType) {
      ParameterizedType that = (ParameterizedType) o;
      if (this == that) return true;

      Type thatOwner   = that.getOwnerType();
      Type thatRawType = that.getRawType();

      /*if (false) {
        boolean ownerEquality = (ownerType == null ? thatOwner == null : ownerType.equals(thatOwner));
        boolean rawEquality = (rawType == null ? thatRawType == null : rawType.equals(thatRawType));
        boolean typeArgEquality = Arrays.equals(actualTypeArguments, that.getActualTypeArguments());
        for (Type t : actualTypeArguments) System.out.printf("\t\t%s%s%n", t, t.getClass());
        System.out.printf("\towner %s\traw %s\ttypeArg %s%n", ownerEquality, rawEquality, typeArgEquality);
        return ownerEquality && rawEquality && typeArgEquality;
      }*/
      return Objects.equals(ownerType, thatOwner) && Objects.equals(rawType, thatRawType) && Arrays.equals(actualTypeArguments, that.getActualTypeArguments());
    }
    return false;
  }

  @Override
  public int hashCode() {
    return Arrays.hashCode(actualTypeArguments) ^ Objects.hashCode(ownerType) ^ Objects.hashCode(rawType);
  }

  public String toString() {
    StringBuilder sb = new StringBuilder();

    if (ownerType != null) {
      if (ownerType instanceof Class) sb.append(((Class<?>) ownerType).getName());
      else sb.append(ownerType.toString());

      sb.append("$");

      if (ownerType instanceof ParameterizedTypeImpl) {
        sb.append(rawType.getName().replace( ((ParameterizedTypeImpl)ownerType).rawType.getName() + "$", ""));
      } else sb.append(rawType.getSimpleName());
    } else sb.append(rawType.getName());

    if (actualTypeArguments != null && actualTypeArguments.length > 0) {
      sb.append("<");
      boolean first = true;
      for (Type t: actualTypeArguments) {
        if (first) first = false;
        else sb.append(", ");
        sb.append(t.toString());
      }
      sb.append(">");
    }

    return sb.toString();
  }
}